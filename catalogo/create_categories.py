import os

import mysql.connector
from unidecode import unidecode
import re
from catalogo.read_csv import read_csv
from catalogo.create_slug import create_slug
import time



def create_categories(db, categories_filename, list_of_categories, category_suffix):
    
    print("111111111111111111111111111111111111111111111111111", list_of_categories)
    count = 0

    if len(categories_filename) > 0:
            # print("DATABASE: ", db)
            
            """
            Search for the last term_id number
            Change the count_list variable before creating the author, language, material type and edition categories

            """
            # count_list = count_list
            
            
            list_of_categories = read_csv(categories_filename)

            for categories in list_of_categories:
                categories_text = " - ".join(filter(None,categories))
                print(categories_text)
                        
                count += 1
                        # count = -1

                slugs_text = ""

                for c in range(len(categories)):
                            
                    if categories[c] != "":
                        category = categories[c]
                        
                        slugs = []
                        for n in range(c, -1, -1):  # Use c here, not count
                            if categories[n] != "":
                                slug = create_slug(categories[n])
                                slug = slug.replace("'", "").replace("-", "")

                                if n != 0:
                                    slugs.append(slug)
                                    slugs.append("-")
                                else:
                                    slugs.append(slug)
                                slugs_text = "".join(slugs) + category_suffix                    
                        # Change before writing the slugs 
                        # to: cat, aut, ed, lang, etc.
                                
                                # if 'images' in categories_filename:
                                #     if 'canto' in categories[0].lower():
                                        
                                #         slugs_text = "".join(slugs) + '_pa_cantos'
                                #     else:
                                #         slugs_text = "".join(slugs) + '_pa_episodios'
                                # elif 'Imagens' in categories:
                                #     slugs_text = "".join(slugs) + ''
                            
                            # print(slugs_text)
                        
                # To avoid writing a second time the first categories that don't exist in the DB
                if slugs_text:
                    # To add the categories list to the Excel, add the count_list variable
                    # print("###", count, category, slugs_text)

                    check_category = db.get_slugs(slugs_text)
                    if check_category:
                        continue
                    
                    db.insert_category(categories_text, slugs_text)
            
    else:
            # list_of_categories = list_of_categories
            # print("LIST: ", list_of_categories)
            # for values in list_of_categories.values():
            name = list_of_categories['term']
            slug = list_of_categories['slug']
            print("CATEGORY: ", name)
            # print("SLUG: ", slug)
            db.insert_category(name, slug)

              

                    