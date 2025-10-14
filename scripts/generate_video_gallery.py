import os
from pathlib import Path
import cv2
from PIL import Image

# Base GitHub raw URL for videos and thumbnails
base_url = "https://github.com/beltedblinds/idols-video-01/raw/refs/heads/main/"
output_file = "idol_video_links.txt"
thumb_root = Path("thumbnails")

def extract_first_frame(video_path, thumb_path):
    """Extract the first frame from a video and save as a .webp thumbnail"""
    try:
        cap = cv2.VideoCapture(str(video_path))
        success, frame = cap.read()
        if success:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.thumbnail((300, 300))
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb_path, "WEBP")
            print(f"✅ Created thumbnail for {video_path}")
        else:
            print(f"⚠️ Could not read frame from {video_path}")
        cap.release()
    except Exception as e:
        print(f"⚠️ Error creating thumbnail for {video_path}: {e}")

processed_thumbs = set()
lines = []

# Walk repo and process videos
for root, _, files in os.walk("."):
    # skip the thumbnails folder itself to avoid scanning generated thumbs as source videos
    if Path(root).resolve() == thumb_root.resolve():
        continue

    for file in files:
        if file.lower().endswith((".mp4", ".mov", ".webm")):
            full_path = Path(root) / file
            relative_path = full_path.relative_to(".")
            # Idol name = top-level folder (or "Unknown" if file at repo root)
            idol_name = relative_path.parts[0] if len(relative_path.parts) > 1 else "Unknown"

            # Desired thumbnail path under thumbnails/<same folder>/<stem>.webp
            thumb_folder = thumb_root / relative_path.parent
            thumb_path = thumb_folder / (full_path.stem + ".webp")

            # Skip generation if thumbnail already exists
            if not thumb_path.exists():
                extract_first_frame(full_path, thumb_path)
            else:
                print(f"⏩ Skipping existing thumbnail for {full_path}")

            # Remember processed thumbs for cleanup later
            processed_thumbs.add(str(thumb_path.resolve()))

            # Build GitHub raw URLs (space -> %20)
            video_url = base_url + str(relative_path).replace(" ", "%20")
            thumb_url = base_url + str(thumb_path).replace(" ", "%20")

            # ✅ Leave category blank (same as idols-media-01)
            lines.append(f"{idol_name}, {video_url}, {thumb_url}, ")

# Sort and write the links file
lines.sort()
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Generated {len(lines)} entries in {output_file}")

# --- Cleanup: remove orphan thumbnails (thumbnails without a corresponding video) ---
removed = 0
if thumb_root.exists():
    for thumb_file in thumb_root.rglob("*.webp"):
        rel = thumb_file.relative_to(thumb_root)  # e.g. "Aespa Karina/video1.webp"
        possible_video_dir = Path(".") / rel.parent  # e.g. "./Aespa Karina"
        stem = thumb_file.stem  # video filename without extension

        # check for any video with the same stem and supported extensions
        found_video = any((possible_video_dir / (stem + ext)).exists() for ext in (".mp4", ".mov", ".webm"))

        if not found_video:
            try:
                thumb_file.unlink()
                removed += 1
                print(f"🗑️ Removed orphan thumbnail: {thumb_file}")
            except Exception as e:
                print(f"⚠️ Failed to remove {thumb_file}: {e}")

print(f"🧹 Cleanup complete — removed {removed} orphan thumbnails.")
