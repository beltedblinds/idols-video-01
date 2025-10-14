import os
import shutil
from pathlib import Path

source_root = Path("idols-media-01")
target_root = Path("idols-video-01")

excluded = {
    ".github/workflows",
    "thumbnails",
    "idol_gallery_links.txt"
}

for root, dirs, files in os.walk(source_root):
    rel = Path(root).relative_to(source_root)
    
    # Skip excluded folders or files
    if any(str(rel).startswith(ex) for ex in excluded):
        continue
    
    # Create corresponding target folder
    target_dir = target_root / rel
    os.makedirs(target_dir, exist_ok=True)
    
    # If directory is empty, add .gitkeep
    if not any(os.scandir(target_dir)):
        (target_dir / ".gitkeep").touch()

print("✅ Folder structure copied successfully with .gitkeep placeholders!")
