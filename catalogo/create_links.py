def generate_resized_image_links(ncb, base_url, output_file="resized_links.txt"):
    # Image sizes from your "Image Sizes" board
    image_sizes = [
        {"name": "medium", "width": 200, "height": 300},
        {"name": "large", "width": 682, "height": 1024},
        {"name": "thumbnail", "width": 150, "height": 150},
        {"name": "medium_large", "width": 768, "height": 1154},
        {"name": "trp-custom-language-flag", "width": 8, "height": 12},
        {"name": "martfury-blog-grid", "width": 380, "height": 300},
        {"name": "martfury-blog-list", "width": 790, "height": 510},
        {"name": "martfury-blog-masonry", "width": 370, "height": 556},
        {"name": "woocommerce_thumbnail", "width": 300, "height": 300},
        {"name": "woocommerce_single", "width": 600, "height": 901},
        {"name": "woocommerce_gallery_thumbnail", "width": 100, "height": 100},
    ]

    # Validate and transform the URL
    if "full/!" not in base_url or "/0/default.jpg" not in base_url:
        raise ValueError("URL format is incorrect or missing expected IIIF segments.")

    # Extract parts before and after the dimensions
    prefix = base_url.split("full/!")[0] + "full/!"
    suffix = "/0/default.jpg"

    with open(output_file, "a") as f:
        for size in image_sizes:
            new_url = f"{prefix}{size['width']},{size['height']}{suffix}"
            to_write = f"{ncb}-{size['width']}x{size['height']};{new_url}\n"
            f.write(to_write)

    # print(f"✅ {len(image_sizes)} links written to '{output_file}'.")

# Example usage
# example_link = "https://bndigital.bnportugal.gov.pt//i/?IIIF=/08/49/1a/3c/08491a3c-7d48-45e2-9f48-ed59247ce3b8/iiif/cam-382-1-p_0001.tif/full/!300,500/0/default.jpg"
# generate_resized_image_links("329076", example_link)
