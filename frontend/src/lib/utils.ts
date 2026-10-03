import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility to merge Tailwind CSS classes conditionally without style conflicts.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Riporta lo scroll in cima alla pagina.
 * Gestisce sia il contenitore principale <main> con scroll interno sia window per dispositivi o layout custom.
 */
export function scrollToTop(smooth: boolean = true) {
  const mainEl = document.querySelector("main")
  if (mainEl) {
    mainEl.scrollTo({ top: 0, behavior: smooth ? "smooth" : "auto" })
  }
  window.scrollTo({ top: 0, behavior: smooth ? "smooth" : "auto" })
}
