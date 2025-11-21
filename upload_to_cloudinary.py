import cloudinary
import cloudinary.uploader
import os

# 1. Configure Cloudinary connection (fill these in from your dashboard)
cloudinary.config(
    cloud_name="dhnqvdn8p",   # e.g. "mydemo123"
    api_key="124483446182699",         # e.g. "1234567890abcdef"
    api_secret="J--wtE9lbWAHpORZztYy1lqKSIQ",   # long secret string
)

# 2. Choose the local image file to upload
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
IMAGE_PATH = os.path.join(STATIC_DIR, "last_visitor.jpg")

# 3. Upload the image
result = cloudinary.uploader.upload(
    IMAGE_PATH,
    folder="smart-doorbell-lab",  # optional logical folder name
)

# 4. Print the secure URL returned by Cloudinary
print("Upload complete.")
print("Public URL:", result["secure_url"])
