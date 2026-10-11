export type ThemeId = "dark-slate" | "oled" | "light"

export interface ThemeConfig {
  id: ThemeId
  name: string
  subtitle: string
  description: string
  icon: "Moon" | "Zap" | "Sun"
  badge: string
  colors: {
    bgPreview: string
    cardPreview: string
    borderPreview: string
    textPreview: string
    accentPreview: string
  }
}

export const THEMES: ThemeConfig[] = [
  {
    id: "dark-slate",
    name: "Dark Slate",
    subtitle: "Ribilanciato",
    description: "Sfondo ardesia profondo, card rialzate ad alto contrasto e accento smeraldo riposante.",
    icon: "Moon",
    badge: "Consigliato",
    colors: {
      bgPreview: "#0a0f1d",
      cardPreview: "#141c2e",
      borderPreview: "#26354f",
      textPreview: "#f8fafc",
      accentPreview: "#10b981",
    },
  },
  {
    id: "oled",
    name: "OLED High-Contrast",
    subtitle: "Nero Assoluto",
    description: "Neri profondi #000000, card grafite nitide e dettagli ad altissima definizione.",
    icon: "Zap",
    badge: "Risparmio Batteria",
    colors: {
      bgPreview: "#000000",
      cardPreview: "#121212",
      borderPreview: "#333333",
      textPreview: "#ffffff",
      accentPreview: "#10b981",
    },
  },
  {
    id: "light",
    name: "Clean Light",
    subtitle: "Luminoso Diurno",
    description: "Sfondo chiaro fresco, card bianche pure e testi scuri ad altissimo contrasto sotto la luce.",
    icon: "Sun",
    badge: "Alta Luminosità",
    colors: {
      bgPreview: "#f8fafc",
      cardPreview: "#ffffff",
      borderPreview: "#cbd5e1",
      textPreview: "#0f172a",
      accentPreview: "#059669",
    },
  },
]
