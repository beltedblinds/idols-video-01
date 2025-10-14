import os
from pathlib import Path
import cv2
from PIL import Image

base_url = "https://github.com/beltedblinds/idols-video-01/raw/refs/heads/main/"
output_file = "idol_video_links.txt"

def extract_first_frame(video_path, thumb_path):
    try:
        cap = cv2.VideoCapture(str(video_path))
        success, frame = cap.read()
        if success:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.thumbnail((300, 300))
            img.save(thumb_path, "WEBP")
            print(f"✅ Created thumbnail for {video_path}")
        else:
            print(f"⚠️ Could not read frame from {video_path}")
        cap.release()
    except Exception as e:
        print(f"⚠️ Error creating thumbnail for {video_path}: {e}")

lines = []
for root, _, files in os.walk("."):
    for file in files:
        if file.lower().endswith((".mp4", ".mov", ".webm")):
            full_path = Path(root) / file
            relative_path = full_path.relative_to(".")
            idol_name = relative_path.parts[0] if len(relative_path.parts) > 1 else "Unknown"

            thumb_folder = Path("thumbnails") / relative_path.parent
            thumb_folder.mkdir(parents=True, exist_ok=True)
            thumb_path = thumb_folder / (full_path.stem + ".webp")

            extract_first_frame(full_path, thumb_path)

            video_url = base_url + str(relative_path).replace(" ", "%20")
            thumb_url = base_url + str(thumb_path).replace(" ", "%20")

            lines.append(f"{idol_name}, {video_url}, {thumb_url}, Video")

lines.sort()
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Generated {len(lines)} entries in {output_file}")
