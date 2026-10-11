import {
  Palette,
  Moon,
  Zap,
  Sun,
  Check,
  Sparkles,
} from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useTheme } from "@/hooks/useTheme"
import type { ThemeId } from "@/types/theme"
import { THEMES } from "@/types/theme"
import { toast } from "sonner"

interface ThemeSelectionModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ThemeSelectionModal({
  open,
  onOpenChange,
}: ThemeSelectionModalProps) {
  const { theme, setTheme } = useTheme()

  const handleSelectTheme = (selectedId: ThemeId) => {
    setTheme(selectedId)
    const selectedObj = THEMES.find((t) => t.id === selectedId)
    toast.success(`Tema impostato: ${selectedObj?.name || selectedId}`, {
      description: "Le preferenze visive sono state salvate in modo permanente.",
    })
  }

  const getThemeIcon = (iconName: string) => {
    switch (iconName) {
      case "Zap":
        return <Zap className="h-4 w-4" />
      case "Sun":
        return <Sun className="h-4 w-4" />
      case "Moon":
      default:
        return <Moon className="h-4 w-4" />
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl bg-card/95 border-border shadow-2xl backdrop-blur-md">
        <DialogHeader className="space-y-1.5 text-left">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Palette className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-lg font-bold tracking-tight">
                Personalizzazione Aspetto & Tema
              </DialogTitle>
              <DialogDescription className="text-xs text-muted-foreground mt-0.5">
                Scegli lo schema di contrasto e luminosità ideale per il tuo schermo.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-3 py-2">
          {THEMES.map((item) => {
            const isSelected = theme === item.id

            return (
              <div
                key={item.id}
                role="button"
                tabIndex={0}
                onClick={() => handleSelectTheme(item.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    handleSelectTheme(item.id)
                  }
                }}
                className={`relative flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-xl border transition-all cursor-pointer text-left select-none gap-3 ${
                  isSelected
                    ? "border-emerald-500 bg-emerald-500/10 shadow-md shadow-emerald-500/10"
                    : "border-border/60 bg-muted/20 hover:border-border hover:bg-muted/40"
                }`}
              >
                {/* Dettagli Tema & Swatch */}
                <div className="flex items-start gap-3.5 min-w-0">
                  {/* Swatch Circolare con Anteprima Colori Reali */}
                  <div
                    className="h-10 w-10 rounded-xl border flex items-center justify-center shrink-0 shadow-sm relative overflow-hidden"
                    style={{
                      backgroundColor: item.colors.bgPreview,
                      borderColor: item.colors.borderPreview,
                    }}
                  >
                    {/* Mini Card interna simulata */}
                    <div
                      className="h-6 w-6 rounded-md flex items-center justify-center border shadow-xs"
                      style={{
                        backgroundColor: item.colors.cardPreview,
                        borderColor: item.colors.borderPreview,
                        color: item.colors.accentPreview,
                      }}
                    >
                      {getThemeIcon(item.icon)}
                    </div>
                  </div>

                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-bold text-foreground">
                        {item.name}
                      </span>
                      <span className="text-xs text-muted-foreground font-medium">
                        • {item.subtitle}
                      </span>
                      {item.badge && (
                        <Badge
                          variant={isSelected ? "success" : "outline"}
                          className="text-[10px] py-0 px-1.5 h-4 gap-1"
                        >
                          {isSelected && <Sparkles className="h-2.5 w-2.5" />}
                          {item.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Indicatore di Selezione */}
                <div className="flex items-center justify-end sm:justify-center self-end sm:self-center shrink-0">
                  <div
                    className={`h-6 w-6 rounded-full border flex items-center justify-center transition-colors ${
                      isSelected
                        ? "border-emerald-500 bg-emerald-500 text-slate-950 font-bold"
                        : "border-muted-foreground/30 bg-transparent text-transparent"
                    }`}
                  >
                    <Check className="h-3.5 w-3.5 stroke-[3]" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-border/60">
          <span className="text-[11px] text-muted-foreground">
            L&apos;anteprima cambia in tempo reale con persistenza salvata.
          </span>
          <Button
            type="button"
            variant="emerald"
            size="sm"
            onClick={() => onOpenChange(false)}
            className="text-xs font-semibold px-4"
          >
            Chiudi
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
