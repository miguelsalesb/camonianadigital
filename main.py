from bd.bd import DatabaseManager
from catalogo.create_categories import create_categories
from catalogo.create_temp_categories import create_temp_categories
from catalogo.create_other_categories import create_other_categories
from catalogo.create_taxonomies import create_taxonomies
from catalogo.create_posts import create_posts
from catalogo.create_terms_relationships import create_terms_relationships
from catalogo.create_posts_images import create_posts_images
from catalogo.create_postmeta_thumbs import create_postmeta_thumbs
from catalogo.create_postmeta_metadata import create_postmeta_metadata
from catalogo.create_csv_with_posts_and_images_map import create_csv_with_posts_and_images
from catalogo.create_other_terms_relationships import create_other_terms_relationships

from imagens.create_temp_categories import img_create_temp_categories
from imagens.create_other_categories import img_create_other_categories

import time

# --- Usage ---
if __name__ == "__main__":
    db = DatabaseManager(
        host="localhost",
        port=3306,
        user="root",
        password="123456"
    )

    try:

        # SQL - delete and auto increment so that the data
        # starts where it should

        db.delete('wordpress', 'wp_terms', 1)
        #DELETE FROM wordpress.wp_terms
        db.auto_increment('wordpress', 'wp_terms', 1)
        #ALTER TABLE wordpress.wp_terms AUTO_INCREMENT = 1

        db.delete('wordpress_temp', 'all_categories', 1)
        db.delete('wordpress_temp', 'img_all_categories', 1)
        #DELETE FROM wordpress_temp.all_categories

        db.delete('wordpress', 'wp_term_taxonomy', 1)
        #DELETE FROM wordpress.wp_term_taxonomy
        db.auto_increment('wordpress', 'wp_term_taxonomy', 1)
        #ALTER TABLE wordpress.wp_term_taxonomy AUTO_INCREMENT = 1

        db.delete('wordpress', 'wp_posts', 5964)
        #DELETE FROM wordpress.wp_posts WHERE ID >= 5964
        db.auto_increment('wordpress', 'wp_posts', 6092)
        #ALTER TABLE wordpress.wp_posts AUTO_INCREMENT = 6092

        db.delete('wordpress', 'wp_term_relationships', 1)
        #DELETE FROM wordpress.wp_term_relationships

        # Desativar a opção “Despejar colunas binárias em notação hexadecimal 
        # (por exemplo, "abc" seria 0x616263)” ao importar o ficheiro SQL
        db.delete('wordpress', 'wp_postmeta', 1)
        #DELETE FROM wordpress.wp_postmeta
        db.auto_increment('wordpress', 'wp_postmeta', 9647)
        #ALTER TABLE wordpress.wp_postmeta AUTO_INCREMENT = 9647


        categories = db.get_categories()
        
        # count_list = 0
        categories_filename = 'catalogo/categories.csv'
        # other_categories_filename = 'other-categories.csv'
        images_categories_filename = 'imagens/categories-images.csv'
        category_suffix = '_cat'

        print("\n\n\nCRIAR CATEGORIAS")
        time.sleep(3)

        create_categories(db, categories_filename, [], category_suffix)
        
        create_temp_categories(db)
       
        create_other_categories(db)



        create_categories(db, images_categories_filename, [], category_suffix)

        img_create_temp_categories(db)
       
        img_create_other_categories(db)



        create_taxonomies(db)
        # the ID (auto-incremented value, should start in 6092 for the catalogo data)
        
        print("\n\n\nCRIAR ARTIGOS")
        time.sleep(3)
              
        create_posts(db, 6092, 'catalogo')
        create_posts(db, 7341, 'imagens')

        print("\n\n\nCRIAR RELAÇÕES ENTRE ARTIGOS E CATEGORIAS")
        time.sleep(3)

        create_terms_relationships(db, 'catalogo')
        create_other_terms_relationships(db, 'catalogo', ['autor', 'tipo de material', 'línguas', 'seculo de publicação', 'data de publicação'])
        create_terms_relationships(db, 'imagens')
        create_other_terms_relationships(db, 'imagens', ['autor', 'tipo de material', 'línguas', 'seculo de publicação', 'data de publicação'])

        print("\n\n\nCRIAR RELAÇÕES ENTRE ARTIGOS E IMAGENS")
        time.sleep(3)

        create_posts_images(db, 'catalogo')
        create_posts_images(db, 'imagens')

        print("\n\n\nCRIAR METADADOS DAS IMAGENS")
        time.sleep(3)

        create_postmeta_thumbs(db, 9647, 'catalogo')
        create_postmeta_thumbs(db, 0, 'imagens')

        create_postmeta_metadata(db, 0, 'catalogo')
        create_postmeta_metadata(db, 0, 'imagens')

        #create_csv_with_posts_and_images(db, 6092)
        
        #print(categories)
        
    finally:
        pass
        #db.close()






