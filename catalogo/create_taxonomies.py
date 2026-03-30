import os
import mysql.connector

# CRIA AS TAXONOMIAS

def create_taxonomies(db):

    categories = db.get_categories()
    count= 0

    if categories: 
        for i in range(len(categories)):
            # count is the same number as the term_id from table wp_items
            count += 1

            slug = categories[i][2].split("-")
            
            term_id = categories[i][0]

            ind = categories[i][2].rfind("_")
            category_type = categories[i][2][ind:]
            
            taxonomy = ""

            if '_cat' in category_type:
                taxonomy = 'product_cat'
            elif '_tag' in categories[i][2]:
                taxonomy = 'product_tag'
            elif '-material' in categories[i][2]:
                taxonomy = 'pa_tipo-de-material'
            elif '_lingua' in categories[i][2]:
                taxonomy = 'pa_lingua'
            elif '_seculo' in categories[i][2]:
                taxonomy = 'pa_seculo'
            elif '_cantos' in categories[i][2]:
                taxonomy = 'pa_cantos'
            elif '_episodios' in categories[i][2]:
                taxonomy = 'pa_episodios'                
            # elif '_ano' in categories[i][2]:
            #     taxonomy = 'pa_ano'
            else:
                # for the image categories = brand category
                taxonomy = ''

            # In order to have two sidebars
            # One with the main categories and its subcategories
            # And another with each of the categories
            # Some categories enter by 'category' and others by 'product_cat'
            if len(slug) <= 1:
                pass
                val = (int(term_id), taxonomy, '', 0, 1)
                db.insert_taxonomy(int(term_id), taxonomy, '', 0, 1)
            
            else:
                parent_slugs = slug[1:]
                parent_slugs_to_search = "-".join(parent_slugs)
                
                parent_id = db.get_slugs(parent_slugs_to_search)
                
                if parent_id:
                    parent_id = parent_id[0][0]
                else:
                    parent_id = 0
                
                val = (int(term_id), taxonomy, '', parent_id, 1)
                print("***", val)
                db.insert_taxonomy(int(term_id), taxonomy, '', parent_id, 1)