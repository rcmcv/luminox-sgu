"""
Importa automaticamente todos os submódulos de models (exceto base/__init__).

Assim, o Alembic "enxerga" todas as tabelas sem precisar
manter uma lista manual de imports.
"""

from importlib import import_module
from pathlib import Path
import pkgutil

# Caminho deste diretório (app/models)
_pkg_path = Path(__file__).resolve().parent

# Lista todos os módulos .py em app/models (exceto base e __init__)
for module_info in pkgutil.iter_modules([str(_pkg_path)]):
    name = module_info.name
    if name in {"base", "__init__"}:
        continue
    # Importa "app.models.<name>"
    import_module(f"{__package__}.{name}")
