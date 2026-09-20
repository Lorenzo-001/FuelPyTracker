import sys
from pathlib import Path

# Assicura che la root di backend sia nel sys.path per import del tipo "from src..."
_backend_root = str(Path(__file__).resolve().parent.parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)
