import { useState, useEffect, useCallback } from "react"
import type { ThemeId, ThemeConfig } from "@/types/theme"
import { THEMES } from "@/types/theme"

const THEME_STORAGE_KEY = "fpt_theme"
const DEFAULT_THEME: ThemeId = "dark-slate"

function applyThemeClasses(theme: ThemeId) {
  if (typeof document === "undefined") return

  const root = document.documentElement
  if (theme === "light") {
    root.className = "theme-light"
  } else if (theme === "oled") {
    root.className = "dark theme-oled"
  } else {
    root.className = "dark theme-slate"
  }
}

export function getStoredTheme(): ThemeId {
  if (typeof window === "undefined") return DEFAULT_THEME
  try {
    const val = localStorage.getItem(THEME_STORAGE_KEY) as ThemeId | null
    if (val === "dark-slate" || val === "oled" || val === "light") {
      return val
    }
  } catch {
    // Ignore storage errors
  }
  return DEFAULT_THEME
}

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeId>(getStoredTheme)

  useEffect(() => {
    // Assicura che le classi siano sincronizzate
    applyThemeClasses(theme)

    // Listener per modifiche in altre tab / finestre
    const handleStorage = (e: StorageEvent) => {
      if (e.key === THEME_STORAGE_KEY && e.newValue) {
        const newTheme = e.newValue as ThemeId
        if (newTheme === "dark-slate" || newTheme === "oled" || newTheme === "light") {
          setThemeState(newTheme)
          applyThemeClasses(newTheme)
        }
      }
    }

    window.addEventListener("storage", handleStorage)
    return () => window.removeEventListener("storage", handleStorage)
  }, [theme])

  const setTheme = useCallback((newTheme: ThemeId) => {
    setThemeState(newTheme)
    applyThemeClasses(newTheme)
    try {
      localStorage.setItem(THEME_STORAGE_KEY, newTheme)
    } catch {
      // Ignore storage errors
    }
  }, [])

  const currentConfig: ThemeConfig =
    THEMES.find((t) => t.id === theme) || THEMES[0]

  return {
    theme,
    setTheme,
    currentConfig,
    themes: THEMES,
  }
}
