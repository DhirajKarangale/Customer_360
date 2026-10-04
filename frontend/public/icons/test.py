from pathlib import Path
from PIL import Image, ImageOps
import shutil

# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = Path(__file__).parent
OUTPUT_DIR = INPUT_DIR / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".ico"}


def get_images():
    return [
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]


def get_image_size(path):
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except Exception:
        return 0, 0


def find_best_square_image(images):
    """Find the best existing square/logo-like image."""
    candidates = []

    for path in images:
        width, height = get_image_size(path)

        if width == 0:
            continue

        ratio = min(width, height) / max(width, height)

        # Prefer square images
        if ratio >= 0.85:
            candidates.append((width * height, path))

    if candidates:
        return max(candidates, key=lambda x: x[0])[1]

    return None


def find_best_wide_image(images):
    """Find the best wide OG/Twitter/banner image."""
    candidates = []

    for path in images:
        width, height = get_image_size(path)

        if width == 0:
            continue

        ratio = width / height

        # Prefer wide images
        if ratio >= 1.5:
            candidates.append((width * height, path))

    if candidates:
        return max(candidates, key=lambda x: x[0])[1]

    return None


def resize_contain(source, size, output):
    """Resize logo without cropping."""
    with Image.open(source) as img:
        img = img.convert("RGBA")
        img.thumbnail(size, Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", size, (0, 0, 0, 0))

        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2

        canvas.alpha_composite(img, (x, y))
        canvas.save(output, "PNG")


def resize_cover(source, size, output):
    """Resize/crop banner to exact dimensions."""
    with Image.open(source) as img:
        img = img.convert("RGB")

        result = ImageOps.fit(
            img,
            size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )

        result.save(output, "PNG", optimize=True)


def create_ico(source, output):
    with Image.open(source) as img:
        img = img.convert("RGBA")

        img.save(
            output,
            format="ICO",
            sizes=[
                (16, 16),
                (32, 32),
                (48, 48),
                (64, 64),
                (96, 96),
                (128, 128),
                (256, 256),
            ],
        )


# ============================================================
# FIND SOURCE IMAGES
# ============================================================

images = get_images()

if not images:
    raise RuntimeError(f"No images found in {INPUT_DIR}")

logo_source = find_best_square_image(images)
banner_source = find_best_wide_image(images)

if not logo_source:
    raise RuntimeError("Could not find a square/logo image.")

if not banner_source:
    raise RuntimeError("Could not find a wide/banner image.")

print(f"Logo source   : {logo_source.name}")
print(f"Banner source : {banner_source.name}")
print()

# ============================================================
# FAVICONS
# ============================================================

resize_contain(
    logo_source,
    (16, 16),
    OUTPUT_DIR / "favicon-16x16.png"
)

resize_contain(
    logo_source,
    (32, 32),
    OUTPUT_DIR / "favicon-32x32.png"
)

resize_contain(
    logo_source,
    (48, 48),
    OUTPUT_DIR / "favicon-48x48.png"
)

resize_contain(
    logo_source,
    (96, 96),
    OUTPUT_DIR / "favicon-96x96.png"
)

create_ico(
    logo_source,
    OUTPUT_DIR / "favicon.ico"
)

# ============================================================
# APPLE
# ============================================================

resize_contain(
    logo_source,
    (180, 180),
    OUTPUT_DIR / "apple-touch-icon.png"
)

# ============================================================
# ANDROID / PWA
# ============================================================

pwa_sizes = [
    72,
    96,
    128,
    144,
    152,
    192,
    384,
    512,
]

for size in pwa_sizes:
    resize_contain(
        logo_source,
        (size, size),
        OUTPUT_DIR / f"icon-{size}x{size}.png"
    )

# Standard manifest names
resize_contain(
    logo_source,
    (192, 192),
    OUTPUT_DIR / "web-app-manifest-192x192.png"
)

resize_contain(
    logo_source,
    (512, 512),
    OUTPUT_DIR / "web-app-manifest-512x512.png"
)

# ============================================================
# MASKABLE PWA ICONS
# ============================================================

# Maskable icons need safe padding.
# We create a slightly smaller logo on a solid background.

def create_maskable(size, output):
    with Image.open(logo_source) as img:
        img = img.convert("RGBA")

        # Background
        canvas = Image.new(
            "RGBA",
            (size, size),
            (5, 25, 70, 255)
        )

        # Safe-zone logo
        target = int(size * 0.70)

        img.thumbnail(
            (target, target),
            Image.Resampling.LANCZOS
        )

        x = (size - img.width) // 2
        y = (size - img.height) // 2

        canvas.alpha_composite(img, (x, y))
        canvas.save(output, "PNG", optimize=True)


create_maskable(
    192,
    OUTPUT_DIR / "maskable-icon-192x192.png"
)

create_maskable(
    512,
    OUTPUT_DIR / "maskable-icon-512x512.png"
)

# ============================================================
# OPEN GRAPH
# ============================================================

resize_cover(
    banner_source,
    (1200, 630),
    OUTPUT_DIR / "og-image.png"
)

# ============================================================
# TWITTER / X
# ============================================================

resize_cover(
    banner_source,
    (1200, 675),
    OUTPUT_DIR / "twitter-image.png"
)

# ============================================================
# LINKEDIN
# ============================================================

resize_cover(
    banner_source,
    (1200, 627),
    OUTPUT_DIR / "linkedin-image.png"
)

# ============================================================
# SQUARE SOCIAL IMAGE
# ============================================================

resize_cover(
    banner_source,
    (1200, 1200),
    OUTPUT_DIR / "social-image-square.png"
)

# ============================================================
# LOGO PNG
# ============================================================

resize_contain(
    logo_source,
    (1024, 1024),
    OUTPUT_DIR / "logo.png"
)

# ============================================================
# SIMPLE SVG WRAPPER
# ============================================================

# Creates an SVG containing the PNG.
# Useful when your project expects a .svg filename.
svg_path = OUTPUT_DIR / "logo.svg"

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="1024"
    height="1024"
    viewBox="0 0 1024 1024">
    <image
        href="logo.png"
        width="1024"
        height="1024"
        preserveAspectRatio="xMidYMid meet"/>
</svg>
"""

svg_path.write_text(svg_content, encoding="utf-8")

# ============================================================
# MANIFEST
# ============================================================

manifest = """{
  "name": "Customer 360",
  "short_name": "Customer 360",
  "icons": [
    {
      "src": "/web-app-manifest-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/web-app-manifest-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/maskable-icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/maskable-icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "theme_color": "#061946",
  "background_color": "#061946",
  "display": "standalone"
}
"""

(OUTPUT_DIR / "site.webmanifest").write_text(
    manifest,
    encoding="utf-8"
)

print("Generated assets:")
for file in sorted(OUTPUT_DIR.iterdir()):
    print(f"  - {file.name}")

print()
print(f"Output directory: {OUTPUT_DIR}")