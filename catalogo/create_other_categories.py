import os
from urllib.parse import urljoin
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import mysql.connector


from catalogo.read_csv import read_csv
from retrieve.retrieve import RetrieveData
from catalogo.create_categories import create_categories


"""

This script gets data from a table where there are
the ncb of the works, the taxonomies defined in the objects dictionnary
and the type of taxonomy

"""

# my_cursor = db.cursor()
def create_other_categories(db):

  types_of_categories = {'tag': 'autor', '_pa_tipo-de-material': 'tipo de material', '_pa_lingua': 'línguas', '_pa_seculo': 'século de publicação', '_pa_ano': 'data de publicação'}
  list_of_categories = {}
  # val_search1 = 'data de publicação'

  for category_suffix, taxonomy in types_of_categories.items():

    get_temp_category = db.get_category_from_temp_categories(taxonomy)

    for row in get_temp_category:
        
        # print("ROW: ", row)
        term = row[2].strip()
        # taxonomy = row[3]
        slug = row[3]

        list_of_categories['term'] = term
        list_of_categories['slug'] = slug

        get_category = db.get_category(term)
        print("CATEGORY: ", term)
        if get_category:
           
           continue
        create_categories(db,'', list_of_categories, category_suffix)
