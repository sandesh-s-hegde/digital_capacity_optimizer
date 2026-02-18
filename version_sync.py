import re
import os

VERSION = "4.2.5"
FILES_TO_UPDATE = {
    "app.py": r'v\d+\.\d+\.\d+',
    "__init__.py": r'__version__ = "\d+\.\d+\.\d+"',
    "pyproject.toml": r'version = "\d+\.\d+\.\d+"',
    "README.md": r'Version: v\d+\.\d+\.\d+'
}


def sync_versions():
    print(f"🔄 Syncing project to Stable Version: {VERSION}")
    for file_path, pattern in FILES_TO_UPDATE.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()

            # Smart replacement based on file type
            if file_path == "__init__.py":
                new_content = re.sub(pattern, f'__version__ = "{VERSION}"', content)
            elif file_path == "pyproject.toml":
                new_content = re.sub(pattern, f'version = "{VERSION}"', content)
            else:
                new_content = re.sub(pattern, f'v{VERSION}', content)

            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"  ✅ Updated {file_path}")
        else:
            print(f"  ⚠️ Skipping {file_path} (Not found)")


if __name__ == "__main__":
    sync_versions()
