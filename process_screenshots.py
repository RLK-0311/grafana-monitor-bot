from pathlib import Path

SCREENSHOT_DIR = Path("screenshots")

images = sorted(
    SCREENSHOT_DIR.glob("*.png")
)

print("=" * 60)

print(f"Found {len(images)} screenshots\n")

for index, image in enumerate(images, start=1):
    print(f"[{index}/{len(images)}]")
    print("Filename :", image.name)
    print("Path     :", image)
    print("-" * 60)

print("Finished processing screenshots.")
