import { useState, useRef } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Camera,
  UploadCloud,
  FileImage,
  Sparkles,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RefreshCw,
} from "lucide-react"
import { useScanReceiptOcr } from "@/hooks/useRefuelings"
import type { OCRScanResponse } from "@/types"
import { toast } from "sonner"

interface ReceiptOcrModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onApplyData: (data: {
    date?: string
    price_per_liter?: number
    total_cost?: number
    liters?: number
    notes?: string
  }) => void
}

export function ReceiptOcrModal({
  open,
  onOpenChange,
  onApplyData,
}: ReceiptOcrModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [ocrResult, setOcrResult] = useState<OCRScanResponse | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scanMutation = useScanReceiptOcr()

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith("image/")) {
      toast.error("Formato file non supportato. Carica un'immagine JPEG, PNG o WebP.")
      return
    }
    setSelectedFile(file)
    setOcrResult(null)

    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0])
    }
  }

  const handleScan = async () => {
    if (!selectedFile) return
    try {
      const res = await scanMutation.mutateAsync(selectedFile)
      setOcrResult(res)
      if (res.success) {
        toast.success("Scontrino scansionato con successo!")
      } else {
        toast.warning(res.raw_text || "Dati parziali rilevati dallo scontrino.")
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Impossibile leggere i dati dallo scontrino"
      toast.error(msg)
    }
  }

  const handleApply = () => {
    if (!ocrResult) return
    onApplyData({
      date: ocrResult.date || undefined,
      price_per_liter: ocrResult.price_per_liter || undefined,
      total_cost: ocrResult.total_cost || undefined,
      liters: ocrResult.liters || undefined,
      notes: ocrResult.station_name || undefined,
    })
    onOpenChange(false)
    // Cleanup
    setSelectedFile(null)
    setPreviewUrl(null)
    setOcrResult(null)
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setOcrResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(val) => {
        if (!val) handleReset()
        onOpenChange(val)
      }}
    >
      <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Camera className="h-5 w-5" />
            </div>
            Scansione Ricevuta o Scontrino
          </DialogTitle>
          <DialogDescription>
            Carica la foto o la scansione del tuo scontrino di rifornimento.
            Il sistema rileverà automaticamente data, litri erogati, prezzo al litro e importo totale.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* File Upload / Drag Zone */}
          {!selectedFile ? (
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragOver(true)
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                dragOver
                  ? "border-emerald-500 bg-emerald-500/10"
                  : "border-border/60 hover:border-emerald-500/50 hover:bg-muted/30"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileChange(e.target.files[0])
                  }
                }}
              />
              <div className="mx-auto w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3">
                <UploadCloud className="h-6 w-6" />
              </div>
              <p className="text-sm font-semibold">Trascina qui l&apos;immagine dello scontrino</p>
              <p className="text-xs text-muted-foreground mt-1">
                oppure clicca per selezionare da file o fotocamera
              </p>
              <div className="flex items-center justify-center gap-2 mt-4 text-[11px] text-muted-foreground">
                <Badge variant="outline" className="text-[10px]">JPEG</Badge>
                <Badge variant="outline" className="text-[10px]">PNG</Badge>
                <Badge variant="outline" className="text-[10px]">WebP</Badge>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Image Preview */}
              <div className="relative rounded-xl overflow-hidden border border-border/60 bg-muted/30 max-h-56 flex items-center justify-center">
                {previewUrl && (
                  <img
                    src={previewUrl}
                    alt="Anteprima scontrino"
                    className="max-h-56 object-contain w-full"
                  />
                )}
                <div className="absolute top-2 right-2 flex items-center gap-1.5">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs bg-background/80 backdrop-blur-sm gap-1"
                    onClick={handleReset}
                    disabled={scanMutation.isPending}
                  >
                    <RefreshCw className="h-3 w-3" />
                    Cambia
                  </Button>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
                <span className="flex items-center gap-1">
                  <FileImage className="h-3.5 w-3.5" />
                  {selectedFile.name}
                </span>
                <span>{(selectedFile.size / 1024).toFixed(0)} KB</span>
              </div>
            </div>
          )}

          {/* OCR Scan Trigger Button */}
          {selectedFile && !ocrResult && (
            <Button
              variant="emerald"
              className="w-full gap-2"
              onClick={handleScan}
              disabled={scanMutation.isPending}
            >
              {scanMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Lettura scontrino in corso...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Leggi Dati Scontrino
                </>
              )}
            </Button>
          )}

          {/* OCR Result Presentation */}
          {ocrResult && (
            <div className="rounded-xl border border-border/60 bg-muted/20 p-4 space-y-3 animate-in fade-in-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {ocrResult.success ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-amber-400" />
                  )}
                  <span className="text-xs font-semibold">
                    {ocrResult.success ? "Dati Riconosciuti" : "Scansione Parziale"}
                  </span>
                </div>
                {ocrResult.station_name && (
                  <Badge variant="outline" className="text-xs text-emerald-300 border-emerald-500/30">
                    {ocrResult.station_name}
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-background/50 border border-border/40">
                  <span className="text-muted-foreground block text-[10px]">Totale Spesa</span>
                  <span className="text-sm font-bold text-emerald-400 font-mono">
                    {ocrResult.total_cost !== null ? `${ocrResult.total_cost.toFixed(2)} €` : "—"}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-background/50 border border-border/40">
                  <span className="text-muted-foreground block text-[10px]">Prezzo al Litro</span>
                  <span className="text-sm font-bold font-mono">
                    {ocrResult.price_per_liter !== null ? `${ocrResult.price_per_liter.toFixed(3)} €/L` : "—"}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-background/50 border border-border/40">
                  <span className="text-muted-foreground block text-[10px]">Litri Erogati</span>
                  <span className="text-sm font-bold font-mono">
                    {ocrResult.liters !== null ? `${ocrResult.liters.toFixed(2)} L` : "—"}
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-background/50 border border-border/40">
                  <span className="text-muted-foreground block text-[10px]">Data Scontrino</span>
                  <span className="text-sm font-bold font-mono">
                    {ocrResult.date || "—"}
                  </span>
                </div>
              </div>

              <Button
                variant="emerald"
                className="w-full gap-2 mt-2"
                onClick={handleApply}
              >
                Applica al Form Rifornimento
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenChange(false)}
          >
            Chiudi
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
