import os
from PIL import Image

SCREENSHOT_DIR = "screenshots"

VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

def get_all_images(folder):
    images = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                full_path = os.path.join(root, file)
                images.append(full_path)

    return images

def validate_images(image_list):
    valid_images = []

    for img_path in image_list:
        try:
            with Image.open(img_path) as img:
                img.verify()  # checks corruption
            valid_images.append(img_path)
        except Exception as e:
            print(f"[INVALID IMAGE] {img_path} -> {e}")

    return valid_images

def main():
    print("Scanning screenshots folder...")

    images = get_all_images(SCREENSHOT_DIR)

    print(f"Total found: {len(images)}")

    valid_images = validate_images(images)

    print(f"Valid images: {len(valid_images)}")

    print("\nSample files:")
    for img in valid_images[:10]:
        print(" -", img)

    # Save list for next phase
    with open("valid_screenshots.txt", "w") as f:
        for img in valid_images:
            f.write(img + "\n")

    print("\nSaved: valid_screenshots.txt")

if __name__ == "__main__":
    main()
