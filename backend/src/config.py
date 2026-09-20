"""
src/config.py — Loader centralizzato per config.toml

Espone:
  - cfg(key_path, fallback=REQUIRED)  → accesso dot-path con fallback e log
  - DEFAULTS                          → namespace tipizzato con tutte le costanti

Comportamento su errore:
  - Chiave mancante nel TOML  → log warning  + ritorna fallback
  - File assente/corrotto      → log critical + usa FALLBACK_CONFIG built-in (no crash)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import toml

logger = logging.getLogger(__name__)

# Percorso del file TOML: due livelli sopra src/config.py → radice del progetto
_CONFIG_PATH = Path(__file__).parent.parent / "config.toml"

# Sentinella per parametro obbligatorio
_REQUIRED = object()

# =============================================================================
# FALLBACK BUILT-IN
# Usato se config.toml è assente o contiene errori di sintassi.
# Dev'essere IDENTICO alla struttura del TOML.
# =============================================================================
_FALLBACK_CONFIG: dict = {
    "app": {"name": "FuelPyTracker"},
    "defaults": {
        "settings": {
            "price_fluctuation_cents":      0.15,
            "max_total_cost":               120.0,
            "max_accumulated_partial_cost": 80.0,
            "reminder_types": [
                "Controllo Livello Olio",
                "Pressione Pneumatici",
                "Liquido Tergicristalli",
                "Inversione Gomme",
            ],
            "maintenance_types": [
                "Tagliando",
                "Gomme",
                "Batteria",
                "Revisione",
                "Bollo",
                "Riparazione",
                "Assicurazione",
                "Altro",
            ],
            "import_limits": {
                "kml_min":   3.0,
                "kml_max":   30.0,
                "kml_error": 50.0,
                "kmd_max":   1000.0,
            },
        }
    },
}

# Cache singleton — caricato una sola volta per processo
_config_cache: Optional[dict] = None


def _load_config() -> dict:
    """Carica e cachea la configurazione. Usa il fallback built-in in caso di errore."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    try:
        parsed = toml.load(_CONFIG_PATH)
        _config_cache = parsed
        logger.debug("config.toml caricato correttamente da %s", _CONFIG_PATH)
    except FileNotFoundError:
        logger.critical(
            "config.toml non trovato in %s. "
            "L'applicazione userà i valori di default built-in. "
            "Crea il file per personalizzare il comportamento.",
            _CONFIG_PATH,
        )
        _config_cache = _FALLBACK_CONFIG
    except toml.TomlDecodeError as exc:
        logger.critical(
            "Errore di sintassi in config.toml: %s. "
            "L'applicazione userà i valori di default built-in.",
            exc,
        )
        _config_cache = _FALLBACK_CONFIG

    return _config_cache


def cfg(key_path: str, fallback: Any = _REQUIRED) -> Any:
    """
    Accede a un valore con notazione dot-path (es. 'defaults.settings.import_limits.kml_min').

    Args:
        key_path: Percorso dot-separated della chiave.
        fallback:  Valore di ritorno se la chiave non esiste.
                   Se omesso e la chiave manca, solleva KeyError.

    Returns:
        Il valore corrispondente nel config o il fallback.
    """
    config = _load_config()
    keys = key_path.split(".")
    val: Any = config
    for k in keys:
        if not isinstance(val, dict) or k not in val:
            if fallback is _REQUIRED:
                raise KeyError(
                    f"Chiave '{key_path}' non trovata in config.toml e nessun fallback fornito."
                )
            logger.warning(
                "Chiave config '%s' non trovata. Uso fallback: %s",
                key_path, fallback,
            )
            return fallback
        val = val[k]
    return val


# =============================================================================
# DEFAULTS — Namespace tipizzato con le costanti pre-estratte
# Usa questi attributi al posto di chiamate cfg() ripetute nel codice.
# =============================================================================

@dataclass(frozen=True)
class _ImportLimits:
    KML_MIN:   float
    KML_MAX:   float
    KML_ERROR: float
    KMD_MAX:   float


@dataclass(frozen=True)
class _SettingsDefaults:
    PRICE_FLUCTUATION_CENTS:      float
    MAX_TOTAL_COST:               float
    MAX_ACCUMULATED_PARTIAL_COST: float
    REMINDER_TYPES:               List[str]
    MAINTENANCE_TYPES:            List[str]
    IMPORT:                       _ImportLimits


@dataclass(frozen=True)
class _Defaults:
    SETTINGS: _SettingsDefaults


def _build_defaults() -> _Defaults:
    """Costruisce il namespace DEFAULTS leggendo dal config caricato."""
    il = _ImportLimits(
        KML_MIN=cfg("defaults.settings.import_limits.kml_min",   3.0),
        KML_MAX=cfg("defaults.settings.import_limits.kml_max",   30.0),
        KML_ERROR=cfg("defaults.settings.import_limits.kml_error", 50.0),
        KMD_MAX=cfg("defaults.settings.import_limits.kmd_max",   1000.0),
    )
    _default_maint = [
        "Tagliando", "Gomme", "Batteria", "Revisione",
        "Bollo", "Riparazione", "Assicurazione", "Altro",
    ]
    sd = _SettingsDefaults(
        PRICE_FLUCTUATION_CENTS=cfg(
            "defaults.settings.price_fluctuation_cents", 0.15),
        MAX_TOTAL_COST=cfg(
            "defaults.settings.max_total_cost", 120.0),
        MAX_ACCUMULATED_PARTIAL_COST=cfg(
            "defaults.settings.max_accumulated_partial_cost", 80.0),
        REMINDER_TYPES=cfg(
            "defaults.settings.reminder_types",
            ["Controllo Livello Olio", "Pressione Pneumatici",
             "Liquido Tergicristalli", "Inversione Gomme"]),
        MAINTENANCE_TYPES=cfg(
            "defaults.settings.maintenance_types",
            _default_maint),
        IMPORT=il,
    )
    return _Defaults(SETTINGS=sd)


# Singleton del namespace — costruito una sola volta all'import del modulo
DEFAULTS: _Defaults = _build_defaults()
