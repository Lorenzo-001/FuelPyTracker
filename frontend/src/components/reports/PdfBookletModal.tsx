import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
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
import { FileText, Loader2, CheckCircle2, ShieldCheck, Sparkles } from "lucide-react"
import { useGeneratePdf } from "@/hooks/useReports"
import { toast } from "sonner"

const pdfSchema = z.object({
  owner_name: z.string().min(2, "Inserisci nome e cognome dell'intestatario"),
  plate: z
    .string()
    .min(3, "La targa deve contenere almeno 3 caratteri")
    .max(20)
    .toUpperCase(),
  car_model: z.string().min(2, "Specifica marca e modello del veicolo"),
  year: z.string().optional(),
})

type PdfFormData = z.infer<typeof pdfSchema>

interface PdfBookletModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  yearsAvailable?: number[]
}

export function PdfBookletModal({
  open,
  onOpenChange,
  yearsAvailable = [],
}: PdfBookletModalProps) {
  const generatePdfMutation = useGeneratePdf()
  const [downloadSuccess, setDownloadSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<PdfFormData>({
    resolver: zodResolver(pdfSchema),
    defaultValues: {
      owner_name: "Proprietario Veicolo",
      plate: "AB123CD",
      car_model: "Auto Principale",
      year: "",
    },
  })

  const onSubmit = async (data: PdfFormData) => {
    try {
      const yearVal = data.year && data.year !== "all" ? parseInt(data.year, 10) : null
      await generatePdfMutation.mutateAsync({
        owner_name: data.owner_name,
        plate: data.plate.toUpperCase().trim(),
        car_model: data.car_model,
        year: yearVal,
      })
      setDownloadSuccess(true)
      toast.success("Libretto Manutenzione Digitale generato e scaricato!")
      setTimeout(() => {
        onOpenChange(false)
        setDownloadSuccess(false)
      }, 1200)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante la compilazione del PDF"
      toast.error(msg)
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(val) => {
        if (!val) {
          reset()
          setDownloadSuccess(false)
        }
        onOpenChange(val)
      }}
    >
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2.5 text-xl font-bold">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <FileText className="h-5 w-5" />
            </div>
            Libretto Manutenzione Digitale
          </DialogTitle>
          <DialogDescription>
            Compila l&apos;anagrafica del veicolo per generare un documento ufficiale in PDF
            completo di scheda tecnica, storico tagliandi e timbro digitale.
          </DialogDescription>
        </DialogHeader>

        {/* Feature Highlights Banner */}
        <div className="p-3.5 rounded-xl bg-gradient-to-r from-rose-500/10 via-amber-500/10 to-transparent border border-rose-500/20 text-xs space-y-1.5">
          <div className="flex items-center gap-1.5 font-semibold text-rose-300">
            <ShieldCheck className="h-4 w-4" />
            <span>Documento Certificato & Stampabile</span>
          </div>
          <p className="text-muted-foreground leading-relaxed">
            Include il registro cronologico di tutti i tagliandi, revisioni e riparazioni,
            ideale da mostrare all&apos;acquirente in caso di vendita o all&apos;assicurazione.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          {/* Owner Name */}
          <div className="space-y-1.5">
            <Label htmlFor="owner_name" className="text-xs font-semibold">
              Intestatario del Veicolo
            </Label>
            <Input
              id="owner_name"
              placeholder="Es. Mario Rossi"
              {...register("owner_name")}
              className="text-sm"
            />
            {errors.owner_name && (
              <p className="text-xs text-rose-400">{errors.owner_name.message}</p>
            )}
          </div>

          {/* Grid: Plate and Model */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="plate" className="text-xs font-semibold">
                Targa Veicolo
              </Label>
              <Input
                id="plate"
                placeholder="Es. AB123CD"
                {...register("plate")}
                className="font-mono uppercase text-sm tracking-wider"
              />
              {errors.plate && (
                <p className="text-xs text-rose-400">{errors.plate.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="car_model" className="text-xs font-semibold">
                Marca & Modello
              </Label>
              <Input
                id="car_model"
                placeholder="Es. Fiat Panda 1.2 Lounge"
                {...register("car_model")}
                className="text-sm"
              />
              {errors.car_model && (
                <p className="text-xs text-rose-400">{errors.car_model.message}</p>
              )}
            </div>
          </div>

          {/* Year selection */}
          <div className="space-y-1.5">
            <Label htmlFor="year" className="text-xs font-semibold">
              Periodo di Riferimento
            </Label>
            <select
              id="year"
              {...register("year")}
              className="flex h-9 w-full rounded-md border border-input bg-background/50 px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="all">Storico Completo (Tutti gli anni)</option>
              {yearsAvailable.map((y) => (
                <option key={y} value={y.toString()}>
                  Anno Solare {y}
                </option>
              ))}
            </select>
            <p className="text-[11px] text-muted-foreground">
              Seleziona se restringere il libretto a un solo anno o includere l&apos;intera vita del veicolo.
            </p>
          </div>

          <DialogFooter className="pt-3 sm:space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting || generatePdfMutation.isPending}
            >
              Annulla
            </Button>
            <Button
              type="submit"
              variant="emerald"
              disabled={isSubmitting || generatePdfMutation.isPending}
              className="gap-2"
            >
              {generatePdfMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Compilazione PDF in corso...
                </>
              ) : downloadSuccess ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                  Scaricato con Successo!
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Genera & Scarica PDF
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
