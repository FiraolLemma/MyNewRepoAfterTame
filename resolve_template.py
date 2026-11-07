
from pathlib import Path
import shutil

file_path = Path("base/templates/base/base.html")

# Keep a backup before making changes
backup_path = file_path.with_suffix(".html.backup")
shutil.copy2(file_path, backup_path)

lines = file_path.read_text(encoding="utf-8").splitlines()
result = []
i = 0
resolved = 0

while i < len(lines):
    if lines[i].startswith("<<<<<<<"):
        resolved += 1
        i += 1

        # Keep the HEAD section
        while i < len(lines) and not lines[i].startswith("======="):
            result.append(lines[i])
            i += 1

        if i >= len(lines):
            raise ValueError("Conflict separator missing")

        i += 1

        # Skip the incoming version
        while i < len(lines) and not lines[i].startswith(">>>>>>>"):
            i += 1

        if i >= len(lines):
            raise ValueError("Conflict ending missing")

        i += 1
    else:
        result.append(lines[i])
        i += 1

file_path.write_text("\n".join(result) + "\n", encoding="utf-8")

print(f"Resolved {resolved} conflict sections.")
print(f"Backup saved at: {backup_path}")
