import os
import re
import logging
from typing import Dict

# Configure enterprise-grade logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Bumped to the new Enterprise Observability Release
VERSION: str = "5.0.0"

FILES_TO_UPDATE: Dict[str, str] = {
    "app.py": r'v\d+\.\d+\.\d+',
    "__init__.py": r'__version__ = "\d+\.\d+\.\d+"',
    "pyproject.toml": r'version = "\d+\.\d+\.\d+"',
    "README.md": r'Version: v\d+\.\d+\.\d+',
    "CITATION.cff": r'version: \d+\.\d+\.\d+'
}


def sync_versions() -> None:
    """Synchronizes the specified release version across all core project files."""
    logger.info("Synchronizing project to stable release version: %s", VERSION)

    for file_path, pattern in FILES_TO_UPDATE.items():
        if not os.path.exists(file_path):
            logger.warning("Skipping %s (File not found)", file_path)
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Route the regex replacement based on file type syntax
        if file_path == "__init__.py":
            new_content = re.sub(pattern, f'__version__ = "{VERSION}"', content)
        elif file_path == "pyproject.toml":
            new_content = re.sub(pattern, f'version = "{VERSION}"', content)
        elif file_path == "CITATION.cff":
            new_content = re.sub(pattern, f'version: {VERSION}', content)
        elif file_path == "README.md":
            new_content = re.sub(pattern, f'Version: v{VERSION}', content)
        else:
            new_content = re.sub(pattern, f'v{VERSION}', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logger.info("Successfully updated %s", file_path)


if __name__ == "__main__":
    sync_versions()
