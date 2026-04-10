import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import re
import csv
from unidecode import unidecode

import functions
from retrieve.retrieve import RetrieveData
# record_type = type of record - either bibliographic or authority


objects = [
        {"name": "ncb", "type": "controlfield", "tag": "001", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "purl", "type": "datafield", "tag": "856", "codes": ["u"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [4, 0], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "tipo de material", "type": "leader", "tag": "", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "línguas", "type": "datafield", "tag": "101", "codes": ["a"], "delimiter": " ; ", "repeatable_field": "no", "repeatable_subfield": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "língua da obra original", "type": "datafield", "tag": "101", "codes": ["c"], "delimiter": " ; ", "repeatable": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título", "type": "datafield", "tag": "200", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "subtítulo", "type": "datafield", "tag": "200", "codes": ["e"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título original", "type": "datafield", "tag": "304", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": ["orig", ".", ":"], "cut_text_before": ""}},
        {"name": "edição", "type": "datafield", "tag": "205", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        # {"name": "lugar da publicação", "type": "datafield", "tag": "210", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "editor", "type": "datafield", "tag": "210", "codes": ["c"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "data de publicação", "type": "datafield", "tag": "100", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [9,13], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "número de páginas", "type": "datafield", "tag": "215", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "data de publicação", "type": "datafield", "tag": "210", "codes": ["d"], "delimiter": "", "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [9,13], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "publication_date_210", "type": "datafield", "tag": "210", "code": "d", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "nome", "type": "datafield", "tag": "700", "codes": ["b"], "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "apelido", "type": "datafield", "tag": "700", "codes": ["a"], "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},

        {"name": "autor", "type": "datafield", "tag": "700", "codes": ["a", "b", "f", "4"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        {"name": "autor organização", "type": "datafield", "tag": "710", "codes": ["a", "b", "4"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                        
        {"name": "co autor pessoas", "type": "datafield", "tag": "701", "codes": ["a", "b", "f", "4"], "delimiter": " ; ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "autor secundários pessoas", "type": "datafield", "tag": "702", "codes": ["a", "b", "f", "4"], "delimiter": " ; ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        {"name": "co autor organização", "type": "datafield", "tag": "711", "codes": ["a", "b", "4"], "delimiter": ". ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        # {"name": "autor secundários organização", "type": "datafield", "tag": "712", "codes": ["a", "b", "4"], "delimiter": ". ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        # {"name": "apelido autor secundário", "type": "datafield", "tag": "702", "code": "a", "repeatable": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "função autor secundário", "type": "datafield", "tag": "702", "code": "4", "repeatable": "yes", "operations": {"filters": ["730"], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "cota", "type": "datafield", "tag": "966", "codes": ["s"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "cover", "type": "datafield", "tag": "", "code": "", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        # {"name": "coleção", "type": "datafield", "tag": "995", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "id persistente", "type": "controlfield", "tag": "003", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # # {"name": "acesso", "type": "datafield", "tag": "958", "codes": ["b"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas gerais", "type": "datafield", "tag": "300", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas título", "type": "datafield", "tag": "304", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas conteúdo", "type": "datafield", "tag": "327", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "sumário", "type": "datafield", "tag": "330", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título uniforme", "type": "datafield", "tag": "500", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título colectivo uniforme", "type": "datafield", "tag": "501", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}}

]



def create_temp_categories(db):

    with open('catalogo/ncb.csv', mode='r', newline='') as file:

        while True:
            
            ncb=file.readline().strip()
            if not ncb:
                break        

            client = RetrieveData()
            root = client.fetch(ncb)
            
            if root is not None:
                # Example: find all datafield elements
                # doc_xml = root.findall(".//unimarc:datafield", RetrieveData.NAMESPACE)
                # Get the leader, controlfields and datafields data
                record_data = functions.get_fields_data_from_xml(root, objects)

                print("\n\n", record_data)
            for key, values in record_data.items():
                # print(key, values)
                if 'purl' in record_data and record_data['purl']:
                    
                    if key != 'ncb' and key != 'purl' and key != 'edição':
                        if len(values) > 0:
                            ncb = record_data["ncb"]
                            
                            # Some fields are repeatable
                            # To divide its data
                            # Which is separated by semicolons
                            # The field values are split
                            if ';' in values:
                                fields_values = values.split(";")

                                for field_value in fields_values:
                                                                        
                                    slug = functions.get_slug(field_value, key)

                                    # There are several types of authors and they all have 'autor' in the key
                                    if 'autor' in key:
                                        val_write = (ncb, field_value.strip(), slug, 'autor')
                                    else:
                                        val_write = (ncb, field_value.strip(), slug, key)

                                    if 'data de publicação' in key:
                                        f_value = functions.convert_to_century(values).strip()
                                        val_write = (ncb, f_value, slug, 'data de publicação')
                                    else:
                                        val_write = (ncb, field_value.strip(), slug, key)                                    

                                    print(val_write)
                                    db.insert_temp_category(*val_write)
                                    
                            else:
                                if len(values) > 0:
                                    
                                    slug = functions.get_slug(values, key)
               
                                    if 'data de publicação' in key:
                                        f_value = functions.convert_to_century(values).strip()
                                        century_write = (ncb, f_value, slug, 'seculo de publicação')
                                        date_write = (ncb, values.strip(), f"{values.strip()}_pa_data", 'data de publicação')
                                    else:
                                        century_write = (ncb, values.strip(), slug, key)
                                        date_write = (ncb, values.strip(), f"{values.strip()}_pa_data", key)
                                        
                                    db.insert_temp_category(*century_write)
                                    
                                    db.insert_temp_category(*date_write)
    
    