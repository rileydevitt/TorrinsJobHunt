import os
import subprocess

def create_icns(input_image, output_icns):
    # Create iconset directory
    iconset_dir = "app_icon.iconset"
    if not os.path.exists(iconset_dir):
        os.makedirs(iconset_dir)

    # Generate different icon sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        # Normal resolution
        subprocess.run([
            "sips", "-z", str(size), str(size),
            input_image,
            "--out", f"{iconset_dir}/icon_{size}x{size}.png"
        ])
        # Retina resolution
        if size * 2 <= 1024:
            subprocess.run([
                "sips", "-z", str(size*2), str(size*2),
                input_image,
                "--out", f"{iconset_dir}/icon_{size}x{size}@2x.png"
            ])

    # Convert iconset to icns
    subprocess.run(["iconutil", "-c", "icns", iconset_dir])

    # Clean up
    subprocess.run(["rm", "-rf", iconset_dir])

    print(f"Icon created successfully: {output_icns}")

# Use torrin.pdf as the input image
create_icns("torrin.pdf", "app_icon.icns") 