import { useState, useEffect } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { AlertTriangle, XCircle, CheckCircle2, Sparkles, Fuel, Wrench, Database } from "lucide-react"

interface ImportRowEditModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  rowIndex: number | null
  type: "fuel" | "maintenance"
  rowData: Record<string, unknown> | null
  onSave: (
    updatedRow: Record<string, unknown>,
    index: number,
    type: "fuel" | "maintenance"
  ) => void
}

export function ImportRowEditModal({
  open,
  onOpenChange,
  rowIndex,
  type,
  rowData,
  onSave,
}: ImportRowEditModalProps) {
  // Campi specifici per Rifornimenti
  const [dateVal, setDateVal] = useState("")
  const [kmVal, setKmVal] = useState<number>(0)
  const [priceVal, setPriceVal] = useState<number>(0)
  const [costVal, setCostVal] = useState<number>(0)
  const [litersVal, setLitersVal] = useState<number>(0)
  const [fullTankVal, setFullTankVal] = useState(true)
  const [noteUserVal, setNoteUserVal] = useState("")

  // Campi specifici per Manutenzioni
  const [maintTypeVal, setMaintTypeVal] = useState("Tagliando")
  const [descVal, setDescVal] = useState("")
  const [expiryKmVal, setExpiryKmVal] = useState<string>("")
  const [expiryDateVal, setExpiryDateVal] = useState<string>("")

  useEffect(() => {
    if (rowData && open) {
      const d = String(rowData.Data || "").split("T")[0]
      setDateVal(d)
      setKmVal(Number(rowData.Km || 0))

      if (type === "fuel") {
        const p = Number(rowData.Prezzo || 0)
        const c = Number(rowData.Costo || 0)
        const l = Number(rowData.Litri || (p > 0 && c > 0 ? c / p : 0))
        setPriceVal(p)
        setCostVal(c)
        setLitersVal(Number(l.toFixed(2)))
        setFullTankVal(Boolean(rowData.Pieno ?? true))
        // Usa esclusivamente la nota personale dell'utente, mai la nota diagnostica di sistema
        const rawUserNote =
          rowData.Note_User !== undefined && rowData.Note_User !== null
            ? String(rowData.Note_User)
            : ""
        const isSysNote =
          rawUserNote.includes("verrà ignorato") || rawUserNote.includes("Record identico")
        setNoteUserVal(isSysNote ? "" : rawUserNote)
      } else {
        setMaintTypeVal(String(rowData.Tipo || "Tagliando"))
        setCostVal(Number(rowData.Costo || 0))
        setDescVal(String(rowData.Descrizione || ""))
        setExpiryKmVal(
          rowData["Scadenza Km"] !== undefined &&
            rowData["Scadenza Km"] !== null &&
            String(rowData["Scadenza Km"]).trim() !== "" &&
            String(rowData["Scadenza Km"]).trim() !== "null"
            ? String(rowData["Scadenza Km"])
            : ""
        )
        setExpiryDateVal(
          rowData["Scadenza Data"] &&
            String(rowData["Scadenza Data"]).trim() !== "" &&
            String(rowData["Scadenza Data"]).trim() !== "null"
            ? String(rowData["Scadenza Data"]).split("T")[0]
            : ""
        )
      }
    }
  }, [rowData, open, type])

  // Calcolo automatico litri per rifornimenti (non editabili manualmente)
  const handlePriceChange = (newPrice: number) => {
    setPriceVal(newPrice)
    if (newPrice > 0 && costVal > 0) {
      setLitersVal(Number((costVal / newPrice).toFixed(2)))
    } else {
      setLitersVal(0)
    }
  }

  const handleCostChange = (newCost: number) => {
    setCostVal(newCost)
    if (type === "fuel") {
      if (priceVal > 0 && newCost > 0) {
        setLitersVal(Number((newCost / priceVal).toFixed(2)))
      } else {
        setLitersVal(0)
      }
    }
  }

  // Pre-validazione inline in tempo reale
  const validationIssues: { type: "error" | "warning"; message: string }[] = []
  if (type === "fuel") {
    if (kmVal <= 0) {
      validationIssues.push({ type: "error", message: "I chilometri totali devono essere maggiori di zero." })
    }
    if (priceVal <= 0) {
      validationIssues.push({ type: "error", message: "Il prezzo al litro deve essere maggiore di zero." })
    } else if (priceVal < 1.10 || priceVal > 2.60) {
      validationIssues.push({
        type: "warning",
        message: `Prezzo al litro insolitamente ${priceVal < 1.10 ? "basso" : "alto"} (${priceVal.toFixed(3)} €/L).`,
      })
    }
    if (costVal <= 0) {
      validationIssues.push({ type: "error", message: "La spesa totale deve essere maggiore di zero." })
    }
    if (litersVal > 120) {
      validationIssues.push({
        type: "error",
        message: `I litri calcolati (${litersVal.toFixed(2)} L) eccedono la capacità massima del serbatoio (120 L).`,
      })
    }
  } else {
    if (kmVal <= 0) {
      validationIssues.push({ type: "error", message: "I chilometri totali devono essere maggiori di zero." })
    }
    if (costVal < 0) {
      validationIssues.push({ type: "error", message: "Il costo dell'intervento non può essere negativo." })
    } else if (
      costVal > 0 &&
      costVal < 15.0 &&
      ["tagliando", "gomme", "freni", "frizione", "distribuzione", "revisione"].includes(
        maintTypeVal.trim().toLowerCase()
      )
    ) {
      validationIssues.push({
        type: "warning",
        message: `Importo molto basso per un intervento di tipo "${maintTypeVal}" (${costVal.toFixed(2)} €).`,
      })
    }
  }

  const hasBlockingErrors = validationIssues.some((i) => i.type === "error")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (rowIndex === null || !rowData) return

    const updated: Record<string, unknown> = {
      ...rowData,
      Data: dateVal,
      Km: kmVal,
      Costo: costVal,
    }

    if (type === "fuel") {
      updated.Prezzo = priceVal
      updated.Litri = litersVal
      updated.Pieno = fullTankVal
      updated.Note_User = noteUserVal
    } else {
      updated.Tipo = maintTypeVal
      updated.Descrizione = descVal
      updated["Scadenza Km"] =
        expiryKmVal && !isNaN(Number(expiryKmVal)) && Number(expiryKmVal) > 0
          ? Number(expiryKmVal)
          : null
      updated["Scadenza Data"] = expiryDateVal && expiryDateVal.trim() !== "" ? expiryDateVal : null
    }

    onSave(updated, rowIndex, type)
    onOpenChange(false)
  }

  const currentStatus = String(rowData?.Stato || "Nuovo")
  const currentNote = String(rowData?.Note || "")
  const renderDiagnosticBanner = () => {
    const s = currentStatus.toLowerCase()
    const dbId = rowData?.db_id ? String(rowData.db_id) : null

    if (s === "modifica") {
      const rawChanges = currentNote.replace(/^(Cambia|Aggiornamenti):\s*/i, "").trim()
      const changedFields = rawChanges ? rawChanges.split(",").map((f) => f.trim()) : []

      return (
        <div className="p-3.5 rounded-xl border border-sky-500/30 bg-sky-500/10 text-sky-200 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-sky-300">
              <Database className="h-4 w-4 text-sky-400 shrink-0" />
              <span>Record già a database {dbId ? `(ID #${dbId})` : ""}</span>
            </div>
            <Badge variant="outline" className="border-sky-500/40 text-sky-300 bg-sky-500/20 text-[10px]">
              Aggiornamento
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 pl-6 text-[11px] text-sky-100/90">
            <span className="text-muted-foreground">Campi con variazioni rispetto al DB:</span>
            {changedFields.length > 0 ? (
              changedFields.map((field, i) => (
                <Badge
                  key={i}
                  variant="secondary"
                  className="bg-sky-500/20 text-sky-200 border-sky-500/30 font-medium text-[10px] py-0 px-1.5"
                >
                  {field}
                </Badge>
              ))
            ) : (
              <span className="font-mono text-sky-200">{currentNote || "Dati aggiornati"}</span>
            )}
          </div>
        </div>
      )
    }

    if (s === "invariato") {
      return (
        <div className="p-3.5 rounded-xl border border-slate-500/30 bg-slate-500/10 text-slate-300 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-slate-200">
              <CheckCircle2 className="h-4 w-4 text-slate-400 shrink-0" />
              <span>Record Identico Già a Database</span>
            </div>
            <Badge variant="outline" className="border-slate-500/40 text-slate-400 bg-slate-500/10 text-[10px]">
              Invariato
            </Badge>
          </div>
          <p className="pl-6 text-[11px] text-muted-foreground leading-relaxed">
            I dati corrispondono esattamente allo storico {dbId ? `(ID #${dbId})` : ""}. Se non effettui modifiche, la riga verrà ignorata all&apos;importazione.
          </p>
        </div>
      )
    }

    if (s === "errore") {
      const cleanReason = currentNote.replace(/^\|\s*/, "").trim()
      return (
        <div className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-200 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-rose-300">
              <XCircle className="h-4 w-4 text-rose-400 shrink-0" />
              <span>Anomalia Bloccante Rilevata</span>
            </div>
            <Badge variant="outline" className="border-rose-500/40 text-rose-400 bg-rose-500/20 text-[10px]">
              Errore
            </Badge>
          </div>
          <p className="pl-6 font-mono text-[11px] text-rose-100 leading-relaxed">
            {cleanReason || "Anomalia di congruenza o parametri fuori scala rilevati dal sistema"}
          </p>
        </div>
      )
    }

    if (s === "warning") {
      return (
        <div className="p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-200 text-xs space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-amber-300">
              <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
              <span>Avviso di Congruenza</span>
            </div>
            <Badge variant="outline" className="border-amber-500/40 text-amber-400 bg-amber-500/20 text-[10px]">
              Warning
            </Badge>
          </div>
          <p className="pl-6 font-mono text-[11px] text-amber-100 leading-relaxed">
            {currentNote || "Parametro superiore alla soglia di riferimento impostata"}
          </p>
        </div>
      )
    }

    // Default: Nuovo record conforme
    return (
      <div className="p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-200 text-xs space-y-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-emerald-300">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>Nuovo Record Conforme</span>
          </div>
          <Badge variant="outline" className="border-emerald-500/40 text-emerald-400 bg-emerald-500/20 text-[10px]">
            Nuovo
          </Badge>
        </div>
        <p className="pl-6 text-[11px] text-emerald-200/80 leading-relaxed">
          I parametri rispettano le regole di validazione e il record è pronto per il salvataggio.
        </p>
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2.5 text-xl font-bold">
            <div className={`p-2 rounded-xl ${type === "fuel" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
              {type === "fuel" ? <Fuel className="h-5 w-5" /> : <Wrench className="h-5 w-5" />}
            </div>
            <span>Modifica Record prima dell&apos;Importazione (Riga #{rowIndex !== null ? rowIndex + 1 : 1})</span>
          </DialogTitle>
          <DialogDescription>
            Correggi i valori digitati erroneamente prima del salvataggio. Le modifiche verranno
            immediatamente rivalutate dai controlli di sicurezza.
          </DialogDescription>
        </DialogHeader>

        {/* Polished Dynamic Diagnostic Banner */}
        {renderDiagnosticBanner()}

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* Top Grid: Date and Km */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="edit-date" className="text-xs font-semibold">
                Data Rilevazione
              </Label>
              <Input
                id="edit-date"
                type="date"
                value={dateVal}
                onChange={(e) => setDateVal(e.target.value)}
                required
                className="text-sm font-mono"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="edit-km" className="text-xs font-semibold">
                Chilometri Totali
              </Label>
              <Input
                id="edit-km"
                type="number"
                value={kmVal || ""}
                onChange={(e) => setKmVal(Number(e.target.value))}
                required
                className="text-sm font-mono"
                placeholder="Es. 120500"
              />
            </div>
          </div>

          {/* Form specific to Fuel */}
          {type === "fuel" ? (
            <>
              {/* Financials Grid: Prezzo, Spesa, Litri */}
              <div className="grid grid-cols-3 gap-2.5 bg-muted/20 p-3 rounded-xl border border-border/40">
                <div className="space-y-1.5">
                  <Label htmlFor="edit-price" className="text-[11px] font-semibold">
                    Prezzo (€/L)
                  </Label>
                  <Input
                    id="edit-price"
                    type="number"
                    step="0.001"
                    value={priceVal || ""}
                    onChange={(e) => handlePriceChange(Number(e.target.value))}
                    required
                    className="text-sm font-mono px-2"
                    placeholder="1.819"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="edit-cost" className="text-[11px] font-semibold text-emerald-400">
                    Spesa Totale (€)
                  </Label>
                  <Input
                    id="edit-cost"
                    type="number"
                    step="0.01"
                    value={costVal || ""}
                    onChange={(e) => handleCostChange(Number(e.target.value))}
                    required
                    className="text-sm font-mono px-2 border-emerald-500/40"
                    placeholder="50.00"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="edit-liters" className="text-[11px] font-semibold text-muted-foreground">
                      Litri Calcolati
                    </Label>
                    <span className="text-[9px] text-muted-foreground/80 font-mono">(Spesa / Prezzo)</span>
                  </div>
                  <Input
                    id="edit-liters"
                    type="number"
                    step="0.01"
                    value={litersVal || ""}
                    readOnly
                    tabIndex={-1}
                    className="text-sm font-mono px-2 bg-muted/40 cursor-not-allowed text-muted-foreground select-none"
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Pieno Checkbox & Note */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-muted/10 border border-border/40">
                <div className="flex items-center gap-2">
                  <input
                    id="edit-full-tank"
                    type="checkbox"
                    checked={fullTankVal}
                    onChange={(e) => setFullTankVal(e.target.checked)}
                    className="h-4 w-4 rounded border-border text-emerald-500 focus:ring-emerald-400"
                  />
                  <Label htmlFor="edit-full-tank" className="text-xs font-semibold cursor-pointer">
                    Serbatoio Pieno Completo (Full-to-Full)
                  </Label>
                </div>
                <Badge variant="outline" className="text-[10px]">
                  {fullTankVal ? "Pieno" : "Parziale"}
                </Badge>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="edit-note" className="text-xs font-semibold">
                  Note Aggiuntive
                </Label>
                <Input
                  id="edit-note"
                  value={noteUserVal}
                  onChange={(e) => setNoteUserVal(e.target.value)}
                  placeholder="Es. Distributore Eni, autostrada..."
                  className="text-sm"
                />
              </div>
            </>
          ) : (
            /* Form specific to Maintenance */
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="edit-maint-type" className="text-xs font-semibold">
                    Tipologia Intervento
                  </Label>
                  <Input
                    id="edit-maint-type"
                    value={maintTypeVal}
                    onChange={(e) => setMaintTypeVal(e.target.value)}
                    required
                    className="text-sm"
                    placeholder="Tagliando, Freni, Gomme..."
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="edit-maint-cost" className="text-xs font-semibold text-amber-400">
                    Costo Totale Intervento (€)
                  </Label>
                  <Input
                    id="edit-maint-cost"
                    type="number"
                    step="0.01"
                    value={costVal || ""}
                    onChange={(e) => setCostVal(Number(e.target.value))}
                    required
                    className="text-sm font-mono border-amber-500/40"
                    placeholder="180.00"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="edit-maint-desc" className="text-xs font-semibold">
                  Descrizione Intervento
                </Label>
                <Input
                  id="edit-maint-desc"
                  value={descVal}
                  onChange={(e) => setDescVal(e.target.value)}
                  placeholder="Dettagli ricambi, officina..."
                  className="text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-muted/20 border border-border/40">
                <div className="space-y-1.5">
                  <Label htmlFor="edit-expiry-km" className="text-[11px] font-semibold">
                    Prossima Scadenza (KM)
                  </Label>
                  <Input
                    id="edit-expiry-km"
                    type="number"
                    value={expiryKmVal}
                    onChange={(e) => setExpiryKmVal(e.target.value)}
                    placeholder="Es. 140000"
                    className="text-sm font-mono"
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="edit-expiry-date" className="text-[11px] font-semibold">
                    Prossima Scadenza (Data)
                  </Label>
                  <Input
                    id="edit-expiry-date"
                    type="date"
                    value={expiryDateVal}
                    onChange={(e) => setExpiryDateVal(e.target.value)}
                    className="text-sm font-mono"
                  />
                </div>
              </div>
            </>
          )}

          {/* Real-time Inline Validation Banner */}
          {validationIssues.length > 0 && (
            <div
              className={`p-3 rounded-xl border text-xs space-y-1.5 ${
                hasBlockingErrors
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                  : "bg-amber-500/10 border-amber-500/30 text-amber-300"
              }`}
            >
              <div className="flex items-center gap-2 font-semibold">
                {hasBlockingErrors ? (
                  <>
                    <XCircle className="h-4 w-4 text-rose-400 shrink-0" />
                    <span>Dati non validi per la conferma:</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />
                    <span>Segnalazioni di congruenza:</span>
                  </>
                )}
              </div>
              <ul className="list-disc list-inside space-y-0.5 pl-1 text-[11px] opacity-90">
                {validationIssues.map((issue, idx) => (
                  <li key={idx}>{issue.message}</li>
                ))}
              </ul>
            </div>
          )}

          <DialogFooter className="pt-3 sm:space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Annulla
            </Button>
            <Button
              type="submit"
              variant={hasBlockingErrors ? "outline" : "emerald"}
              disabled={hasBlockingErrors}
              className="gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Applica Modifiche & Rivalida
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
