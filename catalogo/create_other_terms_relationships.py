import os
import mysql.connector
from unidecode import unidecode
import re

# Reads the slug data and searches for the correspondent slug in the wp_terms table 
# and gets the term_taxonomy_id data
# Reads the ncb data and searches for the correspondent ncb in the camoniana_digital table 
# and gets the id, which corresponds to the wp_posts table ID
# Writes the data in the wp_posts table

def create_other_terms_relationships(db, collection, taxonomies):

  for taxonomy in taxonomies:
    results = db.get_category_from_temp_categories(taxonomy)

    for row in results:
        ncb = row[1]
        slug = row[3]

        # Remove unwanted punctuation: parentheses, commas, periods
        slug = re.sub(r"[(),.?&']", "", slug)
        # Collapse multiple dashes (--- or --) into a single dash
        slug = re.sub(r"-{2,}", "-", slug)
        
        results2 = db.get_id_from_csv_data(collection, ncb)

        if results2:
            object_id = results2[0]['id']
            results3 = db.get_category_from_slug(slug)
        if results3: 
            term_id = results3[0]['term_id']
            print("******", object_id, term_id)
            db.insert_term_relationship(object_id, term_id, 0)







