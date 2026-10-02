"""
Zarządzanie zależnościami Python.
Sprawdza czy biblioteki są zainstalowane, instaluje brakujące.
"""

import subprocess
import sys
import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Z config
REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "jinja2": "jinja2",
    "openpyxl": "openpyxl",
    "pyodbc": "pyodbc",
}


def is_package_installed(package_name: str) -> bool:
    """Sprawdza czy pakiet jest dostępny."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name: str) -> bool:
    """Instaluje pakiet używając pip."""
    try:
        logger.info(f"Instaluję {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "-q"])
        logger.info(f"✅ {package_name} zainstalowany")
        return True
    except subprocess.CalledProcessError:
        logger.error(f"❌ Nie udało się zainstalować {package_name}")
        return False


def check_and_install_dependencies() -> bool:
    """
    Sprawdza wszystkie wymagane pakiety.
    Instaluje brakujące. Zwraca True jeśli wszystko OK.
    """
    missing = []
    for import_name, package_name in REQUIRED_PACKAGES.items():
        if not is_package_installed(import_name):
            missing.append((import_name, package_name))
            logger.warning(f"⚠️  Brakuje pakietu: {import_name}")

    if not missing:
        logger.info("✅ Wszystkie pakiety są zainstalowane")
        return True

    logger.info(f"\n🔧 Instaluję brakujące pakiety ({len(missing)})...")
    success_count = 0
    for import_name, package_name in missing:
        if install_package(package_name):
            success_count += 1

    if success_count == len(missing):
        logger.info("✅ Wszystkie pakiety zainstalowane pomyślnie")
        return True
    else:
        logger.error(f"❌ {len(missing) - success_count} pakiet(ów) nie udało się zainstalować")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = check_and_install_dependencies()
    sys.exit(0 if success else 1)
