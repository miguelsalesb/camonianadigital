import os
import mysql.connector
from datetime import datetime
import unicodedata
import re


def generate_php_serialized_metadata(image_path, filename):
    len_of_file = len(f"{image_path}{filename}.jpg")
    metadata = (
        f'a:6:{{'
        f's:5:"width";i:900;'
        f's:6:"height";i:1352;'
        f's:4:"file";s:{len_of_file}:"{image_path}{filename}.jpg";'
        f's:8:"filesize";i:576366;'
        f's:5:"sizes";a:11:{{'
    )

    sizes = [
        ("medium", f"{filename}-200x300.jpg", 200, 300, 6235),
        ("large", f"{filename}-682x1024.jpg", 682, 1024, 69798),
        ("thumbnail", f"{filename}-150x150.jpg", 150, 150, 3109),
        ("medium_large", f"{filename}-768x1154.jpg", 768, 1154, 86987),
        ("trp-custom-language-flag", f"{filename}-8x12.jpg", 8, 12, 709),
        ("martfury-blog-grid", f"{filename}-380x300.jpg", 380, 300, 12075),
        ("martfury-blog-list", f"{filename}-790x510.jpg", 790, 510, 42277),
        ("martfury-blog-masonry", f"{filename}-370x556.jpg", 370, 556, 19796),
        ("woocommerce_thumbnail", f"{filename}-300x300.jpg", 300, 300, 9556),
        ("woocommerce_single", f"{filename}-600x901.jpg", 600, 901, 54896),
        ("woocommerce_gallery_thumbnail", f"{filename}-100x100.jpg", 100, 100, 1843),
    ]

    for name, file, width, height, filesize in sizes:
        metadata += (
            f's:{len(name)}:"{name}";a:'
            f'{"6" if name == "woocommerce_thumbnail" else "5"}:{{'
            f's:4:"file";s:{len_of_file}:"{file}";'
            f's:5:"width";i:{width};'
            f's:6:"height";i:{height};'
            f's:9:"mime-type";s:10:"image/jpeg";'
            f's:8:"filesize";i:{filesize};'
        )
        if name == "woocommerce_thumbnail":
            metadata += 's:9:"uncropped";b:0;'
        metadata += '}'

    metadata += '}'  # End of sizes

    metadata += (
        ';s:10:"image_meta";a:12:{'
        's:8:"aperture";s:1:"0";'
        's:6:"credit";s:0:"";'
        's:6:"camera";s:0:"";'
        's:7:"caption";s:0:"";'
        's:17:"created_timestamp";s:1:"0";'
        's:9:"copyright";s:0:"";'
        's:12:"focal_length";s:1:"0";'
        's:3:"iso";s:1:"0";'
        's:13:"shutter_speed";s:1:"0";'
        's:5:"title";s:0:"";'
        's:11:"orientation";s:1:"0";'
        's:8:"keywords";a:0:{}'
        '}'
    )
    metadata += '}'
    return metadata


def create_postmeta_metadata(db, id, collection):

    print("COLLECTION: ", collection)
    
    record = {}

    catalogo_path_to_folder = "2025/capas/"
    # imagens_path_to_folder = "2025/imagens/"

    if collection == 'catalogo':
        result = db.get_posts_with_attachment_type(collection)
    
    elif collection == 'imagens1' or collection == 'imagens2':
        result = db.get_posts_with_attachment_type_images(collection)
        
        
    
    print("RESULT: ******************", result)

    for row in result:
        post_id = row['ID']
        ncb = row['post_title']
        print(post_id)

        if collection == 'imagens1' or collection == 'imagens2':
            volume = row['volume']
            imagem = row['imagem']

        # Skip if metadata already exists for this post
        # elif collection == 'catalogo':
        #     existing = db.get_postmeta(post_id)
        #     if existing:
        #         print(f"Skipping post_id {post_id}, metadata already exists")
        #         continue

        print("################################", id, collection)
        if collection == 'catalogo':
            metadata = generate_php_serialized_metadata(catalogo_path_to_folder, str(ncb))

            if len(metadata) > 0:
                db.insert_post_metadata(post_id, "_wp_attached_file", f"{catalogo_path_to_folder}{ncb}.jpg")
                db.insert_post_metadata(post_id, "_wp_attachment_metadata", metadata)
                db.insert_post_metadata(post_id, "_wp_attachment_image_alt", "Capa da obra")

        elif collection == 'imagens1' or collection == 'imagens2':
                metadata = generate_php_serialized_metadata('2025/imagens/', str(ncb))
                db.insert_post_metadata(post_id, "_wp_attached_file", f"2025/capas/{ncb}.jpg")
                db.insert_post_metadata(post_id, "_wp_attachment_metadata", metadata)
                db.insert_post_metadata(post_id, "_wp_attachment_image_alt", "página")
            
            
        print("\n", metadata)







	