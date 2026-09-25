import { useState, useEffect, useRef, useMemo } from "react"
import { Car, ChevronDown, Check, Search, Sparkles, Pencil, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  POPULAR_VEHICLE_BRANDS,
  guessBrandAndModel,
  type VehicleBrand,
} from "@/data/vehicles"

interface VehicleSelectorProps {
  value: string
  onChange: (val: string) => void
  error?: string
}

export function VehicleSelector({ value, onChange, error }: VehicleSelectorProps) {
  // Mode: "catalog" (Smart Combobox) vs "manual" (Free text input)
  const [mode, setMode] = useState<"catalog" | "manual">("catalog")

  // State for guided selection
  const [selectedBrand, setSelectedBrand] = useState<string>("")
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [customBrand, setCustomBrand] = useState<string>("")
  const [customModel, setCustomModel] = useState<string>("")
  const [extraDetails, setExtraDetails] = useState<string>("")

  // Dropdown open states
  const [brandDropdownOpen, setBrandDropdownOpen] = useState(false)
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false)

  // Search queries for dropdowns
  const [brandSearch, setBrandSearch] = useState("")
  const [modelSearch, setModelSearch] = useState("")

  const brandRef = useRef<HTMLDivElement>(null)
  const modelRef = useRef<HTMLDivElement>(null)

  // Parse helper to extract state from value string
  const syncFromValue = (str: string) => {
    if (!str) return
    const guessed = guessBrandAndModel(str)
    if (guessed.brand) {
      setSelectedBrand(guessed.brand)
      setSelectedModel(guessed.model || (guessed.extra ? "__custom__" : ""))
      if (!guessed.model && guessed.extra) {
        setCustomModel(guessed.extra)
        setExtraDetails("")
      } else {
        setExtraDetails(guessed.extra)
        setCustomModel("")
      }
      setCustomBrand("")
    } else {
      setSelectedBrand("__custom__")
      setCustomBrand(str)
      setSelectedModel("")
      setCustomModel("")
      setExtraDetails("")
    }
  }

  // Initialize from value on mount or external changes
  useEffect(() => {
    if (value) {
      const guessed = guessBrandAndModel(value)
      if (guessed.brand) {
        syncFromValue(value)
      } else {
        setMode("manual")
      }
    }
  }, [value]) // Synchronize when value changes

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (brandRef.current && !brandRef.current.contains(event.target as Node)) {
        setBrandDropdownOpen(false)
      }
      if (modelRef.current && !modelRef.current.contains(event.target as Node)) {
        setModelDropdownOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // Filtered brands
  const filteredBrands = useMemo(() => {
    if (!brandSearch.trim()) return POPULAR_VEHICLE_BRANDS
    const q = brandSearch.toLowerCase()
    return POPULAR_VEHICLE_BRANDS.filter((b) => b.brand.toLowerCase().includes(q))
  }, [brandSearch])

  // Current brand object
  const currentBrandObj = useMemo<VehicleBrand | undefined>(() => {
    return POPULAR_VEHICLE_BRANDS.find((b) => b.brand === selectedBrand)
  }, [selectedBrand])

  // Filtered models
  const filteredModels = useMemo(() => {
    if (!currentBrandObj) return []
    if (!modelSearch.trim()) return currentBrandObj.models
    const q = modelSearch.toLowerCase()
    return currentBrandObj.models.filter((m) => m.toLowerCase().includes(q))
  }, [currentBrandObj, modelSearch])

  const handleSelectBrand = (brand: string) => {
    setSelectedBrand(brand)
    setSelectedModel("")
    setCustomModel("")
    setBrandDropdownOpen(false)
    setBrandSearch("")

    const finalBrand = brand === "__custom__" ? customBrand.trim() : brand
    const parts: string[] = []
    if (finalBrand) parts.push(finalBrand)
    if (extraDetails.trim()) parts.push(extraDetails.trim())
    onChange(parts.join(" ").trim() || "Il mio Veicolo")
  }

  const handleSelectModel = (model: string) => {
    setSelectedModel(model)
    setModelDropdownOpen(false)
    setModelSearch("")

    const finalBrand = selectedBrand === "__custom__" ? customBrand.trim() : selectedBrand
    const finalModel = model === "__custom__" ? customModel.trim() : model
    const parts: string[] = []
    if (finalBrand) parts.push(finalBrand)
    if (finalModel) parts.push(finalModel)
    if (extraDetails.trim()) parts.push(extraDetails.trim())
    onChange(parts.join(" ").trim() || "Il mio Veicolo")
  }

  const handleExtraChange = (extra: string) => {
    setExtraDetails(extra)

    const finalBrand = selectedBrand === "__custom__" ? customBrand.trim() : selectedBrand
    const finalModel = selectedModel === "__custom__" ? customModel.trim() : selectedModel
    const parts: string[] = []
    if (finalBrand) parts.push(finalBrand)
    if (finalModel) parts.push(finalModel)
    if (extra.trim()) parts.push(extra.trim())
    onChange(parts.join(" ").trim() || "Il mio Veicolo")
  }

  const handleCustomBrandChange = (cBrand: string) => {
    setCustomBrand(cBrand)

    const finalBrand = cBrand.trim()
    const finalModel = selectedModel === "__custom__" ? customModel.trim() : selectedModel
    const parts: string[] = []
    if (finalBrand) parts.push(finalBrand)
    if (finalModel) parts.push(finalModel)
    if (extraDetails.trim()) parts.push(extraDetails.trim())
    onChange(parts.join(" ").trim() || "Il mio Veicolo")
  }

  const handleCustomModelChange = (cModel: string) => {
    setCustomModel(cModel)

    const finalBrand = selectedBrand === "__custom__" ? customBrand.trim() : selectedBrand
    const finalModel = cModel.trim()
    const parts: string[] = []
    if (finalBrand) parts.push(finalBrand)
    if (finalModel) parts.push(finalModel)
    if (extraDetails.trim()) parts.push(extraDetails.trim())
    onChange(parts.join(" ").trim() || "Il mio Veicolo")
  }

  const handleSwitchToCatalog = () => {
    setMode("catalog")
    syncFromValue(value)
  }

  const handleSwitchToManual = () => {
    setMode("manual")
  }


  return (
    <div className="space-y-2.5">
      {/* Header with Mode Toggle */}
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
          <Car className="h-3.5 w-3.5 text-emerald-400" />
          <span>Modello Veicolo</span>
          <span className="text-destructive">*</span>
        </label>

        <div className="flex items-center gap-1 bg-muted/40 p-0.5 rounded-lg border border-border/50 text-[11px]">
          <button
            type="button"
            onClick={handleSwitchToCatalog}
            className={`px-2 py-0.5 rounded-md font-medium transition-colors flex items-center gap-1 ${
              mode === "catalog"
                ? "bg-background text-emerald-400 shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Sparkles className="h-3 w-3" />
            <span>Catalogo</span>
          </button>
          <button
            type="button"
            onClick={handleSwitchToManual}
            className={`px-2 py-0.5 rounded-md font-medium transition-colors flex items-center gap-1 ${
              mode === "manual"
                ? "bg-background text-emerald-400 shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Pencil className="h-3 w-3" />
            <span>Testo Libero</span>
          </button>
        </div>
      </div>

      {mode === "manual" ? (
        /* Manual input mode */
        <div className="space-y-1">
          <Input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Es. BMW Serie 1 118d, Fiat Panda 1.2, Moto Yamaha MT-07..."
            className="text-xs"
          />
          <p className="text-[10px] text-muted-foreground">
            Modalità libera attiva: puoi inserire qualsiasi marca, allestimento o tipologia (auto, moto, furgone).
          </p>
        </div>
      ) : (
        /* Guided Smart Combobox mode */
        <div className="space-y-3 p-3 rounded-xl bg-muted/15 border border-border/50">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {/* Selettore Marca */}
            <div className="space-y-1 relative" ref={brandRef}>
              <span className="text-[11px] font-medium text-muted-foreground">
                1. Marca Auto
              </span>

              <button
                type="button"
                onClick={() => setBrandDropdownOpen(!brandDropdownOpen)}
                className="w-full flex items-center justify-between px-3 py-2 text-xs rounded-md border border-input bg-background/80 hover:bg-background transition-colors text-left"
              >
                <span className={selectedBrand ? "font-medium text-foreground" : "text-muted-foreground"}>
                  {selectedBrand === "__custom__"
                    ? "Altra marca (personalizzata)"
                    : selectedBrand || "Seleziona Marca..."}
                </span>
                <ChevronDown className="h-3.5 w-3.5 opacity-60 shrink-0" />
              </button>

              {/* Brand Dropdown Menu */}
              {brandDropdownOpen && (
                <div className="absolute top-full left-0 mt-1 w-full z-50 rounded-lg border border-border/80 bg-popover/95 backdrop-blur-md shadow-xl text-popover-foreground overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                  <div className="p-1.5 border-b border-border/50 flex items-center gap-1.5">
                    <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0 ml-1" />
                    <input
                      type="text"
                      placeholder="Cerca marca..."
                      value={brandSearch}
                      onChange={(e) => setBrandSearch(e.target.value)}
                      className="w-full bg-transparent text-xs py-1 outline-none placeholder:text-muted-foreground"
                      autoFocus
                    />
                    {brandSearch && (
                      <button
                        type="button"
                        onClick={() => setBrandSearch("")}
                        className="p-1 hover:text-foreground text-muted-foreground"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </div>

                  <div className="max-h-48 overflow-y-auto p-1 text-xs divide-y divide-border/20">
                    {filteredBrands.map((b) => (
                      <button
                        key={b.brand}
                        type="button"
                        onClick={() => handleSelectBrand(b.brand)}
                        className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-emerald-500/10 hover:text-emerald-400 text-left transition-colors"
                      >
                        <span>{b.brand}</span>
                        {selectedBrand === b.brand && (
                          <Check className="h-3.5 w-3.5 text-emerald-400" />
                        )}
                      </button>
                    ))}

                    <button
                      type="button"
                      onClick={() => handleSelectBrand("__custom__")}
                      className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-muted text-left text-muted-foreground hover:text-foreground transition-colors italic"
                    >
                      <span>Altra marca non in elenco...</span>
                      {selectedBrand === "__custom__" && (
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {selectedBrand === "__custom__" && (
                <Input
                  placeholder="Digita il nome della marca..."
                  value={customBrand}
                  onChange={(e) => handleCustomBrandChange(e.target.value)}
                  className="text-xs mt-1"
                />
              )}
            </div>

            {/* Selettore Modello */}
            <div className="space-y-1 relative" ref={modelRef}>
              <span className="text-[11px] font-medium text-muted-foreground">
                2. Modello
              </span>

              <button
                type="button"
                disabled={!selectedBrand}
                onClick={() => setModelDropdownOpen(!modelDropdownOpen)}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs rounded-md border border-input text-left transition-colors ${
                  !selectedBrand
                    ? "opacity-50 cursor-not-allowed bg-muted/30"
                    : "bg-background/80 hover:bg-background"
                }`}
              >
                <span className={selectedModel ? "font-medium text-foreground" : "text-muted-foreground"}>
                  {selectedModel === "__custom__"
                    ? "Altro modello (personalizzato)"
                    : selectedModel || (selectedBrand ? "Seleziona Modello..." : "Prima scegli una marca")}
                </span>
                <ChevronDown className="h-3.5 w-3.5 opacity-60 shrink-0" />
              </button>

              {/* Model Dropdown Menu */}
              {modelDropdownOpen && selectedBrand && (
                <div className="absolute top-full left-0 mt-1 w-full z-50 rounded-lg border border-border/80 bg-popover/95 backdrop-blur-md shadow-xl text-popover-foreground overflow-hidden animate-in fade-in zoom-in-95 duration-100">
                  <div className="p-1.5 border-b border-border/50 flex items-center gap-1.5">
                    <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0 ml-1" />
                    <input
                      type="text"
                      placeholder="Cerca modello..."
                      value={modelSearch}
                      onChange={(e) => setModelSearch(e.target.value)}
                      className="w-full bg-transparent text-xs py-1 outline-none placeholder:text-muted-foreground"
                      autoFocus
                    />
                    {modelSearch && (
                      <button
                        type="button"
                        onClick={() => setModelSearch("")}
                        className="p-1 hover:text-foreground text-muted-foreground"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </div>

                  <div className="max-h-48 overflow-y-auto p-1 text-xs divide-y divide-border/20">
                    {filteredModels.map((m) => (
                      <button
                        key={m}
                        type="button"
                        onClick={() => handleSelectModel(m)}
                        className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-emerald-500/10 hover:text-emerald-400 text-left transition-colors"
                      >
                        <span>{m}</span>
                        {selectedModel === m && (
                          <Check className="h-3.5 w-3.5 text-emerald-400" />
                        )}
                      </button>
                    ))}

                    <button
                      type="button"
                      onClick={() => handleSelectModel("__custom__")}
                      className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-md hover:bg-muted text-left text-muted-foreground hover:text-foreground transition-colors italic"
                    >
                      <span>Altro modello non in elenco...</span>
                      {selectedModel === "__custom__" && (
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {selectedModel === "__custom__" && (
                <Input
                  placeholder="Digita il nome del modello..."
                  value={customModel}
                  onChange={(e) => handleCustomModelChange(e.target.value)}
                  className="text-xs mt-1"
                />
              )}
            </div>
          </div>

          {/* Dettagli Opzionali (Allestimento / Motorizzazione) */}
          <div className="space-y-1">
            <span className="text-[11px] font-medium text-muted-foreground">
              3. Versione o Allestimento opzionale
            </span>
            <Input
              placeholder="Es. 118d Msport, 1.2 Fire 69cv, Lounge, Long Range..."
              value={extraDetails}
              onChange={(e) => handleExtraChange(e.target.value)}
              className="text-xs bg-background/80"
            />
          </div>

          {/* Live Preview Badge */}
          <div className="flex items-center justify-between pt-1 border-t border-border/30 text-xs">
            <span className="text-[11px] text-muted-foreground">Risultato assegnato:</span>
            <Badge variant="outline" className="font-semibold text-emerald-400 border-emerald-500/30 bg-emerald-500/10">
              {value || "Nessun veicolo"}
            </Badge>
          </div>
        </div>
      )}

      {error && <p className="text-[11px] text-destructive">{error}</p>}
    </div>
  )
}
