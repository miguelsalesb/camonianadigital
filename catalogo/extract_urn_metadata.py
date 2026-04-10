import os
import sqlite3
import time
import ssl
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import re
import datetime
import dates
import convert_to_json
#import elasticsearch_export
import extract_bnd_cover_link
import export_to_csv
import gc
import csv
from dates import get_dates
import create_links


import sys


# record_type = type of record - either bibliographic or authority

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://urn.bnportugal.gov.pt/ncb/unimarc/marcxchange?id="
NAMESPACE = {'unimarc': 'info:lc/xmlns/marcxchange-v2'}

date_today = datetime.date.today()

COLLECTION = "CAM500"
CONDITION = 'purl'

JSON_FILE_PATH = 'data.json'
INDEX = 'camoniana'

objects = [
        {"name": "ncb", "type": "controlfield", "tag": "001", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "purl", "type": "datafield", "tag": "856", "codes": ["u"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [4, 0], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "tipo de material", "type": "leader", "tag": "", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "línguas", "type": "datafield", "tag": "101", "codes": ["a", "c"], "delimiter": " ; ", "repeatable_field": "no", "repeatable_subfield": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "língua da obra original", "type": "datafield", "tag": "101", "codes": ["c"], "delimiter": " ; ", "repeatable": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "título", "type": "datafield", "tag": "200", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "subtítulo", "type": "datafield", "tag": "200", "codes": ["e"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "título original", "type": "datafield", "tag": "304", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": ["orig", ".", ":"], "cut_text_before": ""}},
        {"name": "edição", "type": "datafield", "tag": "205", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        {"name": "publicação", "type": "datafield", "tag": "210", "codes": ["a", "c"], "delimiter": " : ", "repeatable_field": "no", "repeatable_subfield": "yes","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "lugar da publicação", "type": "datafield", "tag": "210", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no","operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "editor", "type": "datafield", "tag": "210", "codes": ["c"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "data de publicação", "type": "datafield", "tag": "100", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [9,13], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "número de páginas", "type": "datafield", "tag": "215", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "data de publicação", "type": "datafield", "tag": "210", "codes": ["d"], "delimiter": "", "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [9,13], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "publication_date_210", "type": "datafield", "tag": "210", "code": "d", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "nome", "type": "datafield", "tag": "700", "codes": ["b"], "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "apelido", "type": "datafield", "tag": "700", "codes": ["a"], "repeatable": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},

        {"name": "autor", "type": "datafield", "tag": "700", "codes": ["a", "b", "f", "4"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        {"name": "autores organização", "type": "datafield", "tag": "710", "codes": ["a", "b", "4"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                        
        {"name": "co-autores pessoas", "type": "datafield", "tag": "701", "codes": ["a", "b", "f", "4"], "delimiter": " ; ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "autores secundários pessoas", "type": "datafield", "tag": "702", "codes": ["a", "b", "f", "4"], "delimiter": " ; ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        {"name": "co-autores organizações", "type": "datafield", "tag": "711", "codes": ["a", "b", "4"], "delimiter": ". ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        {"name": "autores secundários organizações", "type": "datafield", "tag": "712", "codes": ["a", "b", "4"], "delimiter": ". ", "repeatable_field": "yes", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},                                                                                
        # {"name": "apelido autor secundário", "type": "datafield", "tag": "702", "code": "a", "repeatable": "yes", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "função autor secundário", "type": "datafield", "tag": "702", "code": "4", "repeatable": "yes", "operations": {"filters": ["730"], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "cota", "type": "datafield", "tag": "966", "codes": ["s"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "cover", "type": "datafield", "tag": "", "code": "", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},        
        {"name": "coleção", "type": "datafield", "tag": "995", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "id persistente", "type": "controlfield", "tag": "003", "codes": [""], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        {"name": "acesso", "type": "datafield", "tag": "958", "codes": ["b"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas gerais", "type": "datafield", "tag": "300", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas título", "type": "datafield", "tag": "304", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "notas conteúdo", "type": "datafield", "tag": "327", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "sumário", "type": "datafield", "tag": "330", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título uniforme", "type": "datafield", "tag": "500", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}},
        # {"name": "título colectivo uniforme", "type": "datafield", "tag": "501", "codes": ["a"], "delimiter": "", "repeatable_field": "no", "repeatable_subfield": "no", "operations": {"filters": [], "get_subfield_with_specific_indicators": [], "get_substring": [], "cut_text_after_chars": [], "cut_text_before": ""}}

]

def open_file(filename, mode):
        try:
            return open(filename, mode=mode)
        except:
            return None

def create_report():
    # Create a report file
    if not os.path.exists('relatorio.csv'):    
        return open('relatorio.csv', mode='a', encoding='utf-8')
        
def save_error(e):
    f_report.write()
    f_report.flush()    

# Create a report file
# if not os.path.exists('errors.csv'):    
#     f_errors = open('errors.csv', 'w', encoding='utf-8')
#     f_errors.write(f'Relatório de {date_today}')
#     f_errors.flush()
# else: 
#     f_errors = open('errors.csv', 'a')
#     f_errors.write(f'Relatório de {date_today}')


def cut_text_after_chars(field_data, object_elements_list, xml_parameters=[]):
    
    # Check if field data has the elements that are to be removed
    # and only remove it if it has
    
    res = [ele for ele in field_data if(ele in object_elements_list)]
    
    if res == True:
        for word in object_elements_list:
            orig_index = field_data.rfind(word)
            
            if orig_index == -1:
                continue  # If the word is not found, skip to the next word

            g_index = orig_index + field_data[orig_index:].find(word[-1])
            new_data = field_data[g_index+1:]
    # If the field data doesn't have any of the object_elements_list
    # then there is no original title in the data field
    else:
        new_data = ""

    return new_data
    

def keep_common_text(field_data):
    data = []
    data.append(field_data)
    
    common_words = os.path.commonprefix(field_data)

    return common_words



def get_substring(field_data, substring_positions, xml_parameters=[]):
    
    data = field_data[int(substring_positions[0]):int(substring_positions[1])]

    return data


def cut_string_with_more_than_200_chars(data):
    
    field_data = f"{data[:197]}..."
    
    title_list = data.split(" ")
    title_list

    # The Wordpress title field only supports 200 characters

    return field_data


def get_subfield_with_specific_indicators(field_data, object_indicators, xml_doc_indicators):

    # In this situation, there is the need to get the field data
    # that has 'purl' in the URL, since only those are links to
    # the digital library
    
    data = ""    
    if 'purl' in field_data:
        field_data_list = []

        if int(object_indicators[0]) == int(xml_doc_indicators[0]) and int(object_indicators[1]) == int(xml_doc_indicators[1]):
            field_data_list.append(field_data.strip())
            
        data = keep_common_text(field_data_list)
        data = "".join(data)

    return data

# The material type is registerd in the leader field
# in a letter code
def get_material_type(leader):
    
    material_type = ""
    # leader = doc_xml.findall('.//unimarc:leader', NAMESPACE)
    char1 = leader[6:7]
    char2 = leader[7:8]

    # print("char1: ", char1)
    # print("char2: ", char2)
    
    if char2 == "s":
        material_type = "Periódico"
    elif char1 == "e" or char1 == "f":
        material_type = "Cartografia"
    elif (char1 == "k"):
        material_type = "Iconografia"
    elif (char1 == "a" or char2 == "c"):
        material_type = "Livro impresso"
    elif (char1 == "b"):
        material_type = "Livro manuscrito"
    elif (char1 == "c" or char1 == "d"):
        material_type = "Partitura"
    elif (char1 == "l"):
        material_type = "Recurso eletrónico"
    elif (char1 == "m"):
        material_type = "Multimédia"
    elif (char1 == "g"):
        material_type = "Vídeo"
    elif (char1 == "i" or char1 == "j"):
        material_type = "Áudio"
    else:
        material_type = "Desconhecido"

    return material_type

# def join_data(data):

#     return_data = {}
#     author = []
#     author_secondary = []

#     for key, value in data.items():
#         if key == 'nome':
#             author.append(value)
#         if key == 'apelido':
#             author.append(value)

#         if key == 'nome_autor_secundário':
#             author_secondary.append(value)
#         if key == 'apelido_autor_secundário':
#             author_secondary.append(value)
    
#     return_data["autor"] = " ".join(author)
#     return_data["autor_secondary"] = " ".join(author_secondary)

#     return return_data

def get_leader_data(leader_data):
    leader_str = ""
    for leader in leader_data:
        leader_str = get_material_type(leader.text)
        
    return leader_str


def get_bnd_link():
    pass


def get_relator_code_str(relator_code_num):
    relator_code = ""
    
    # Open the csv that contains the numeric and textual relator codes
    with open('lista-codigos-funcao.csv', mode='r', newline='') as file:
    
        csv_reader = csv.reader(file, delimiter=';')
    
        for line in csv_reader:
            code_in_line = line[0]
            function_in_line = line[1]

            # for code in relator_codes_num:
            if relator_code_num == code_in_line:
                relator_code = function_in_line

    return relator_code


def get_language(language_code):
    language = ""
    
    # Open the csv that contains the numeric and textual relator codes
    with open('lista-línguas.csv', mode='r', newline='') as file:
    
        csv_reader = csv.reader(file, delimiter=';')
    
        for line in csv_reader:
            code_in_line = line[0]
            
            language_in_line = line[1]

            # for code in relator_codes_num:
            if language_code == code_in_line:
                language = language_in_line

    return language



def get_xml_codes(subfields, tag, predefined_codes):

    for subfield in subfields:
        xml_codes = subfield.get('code')    
        predefined_codes.append(xml_codes)
 
    return predefined_codes


def get_repeated_field_data(datafields, tag, codes, delimiter):
    
    result_list = []
    result = ""
    all_b_values = []
    # Track the current dictionary to build
    current_dict = {}
    all_b_values = []

    for datafield in datafields:
        datafield_tag = datafield.get('tag')

        if datafield_tag == tag:
            subfields = datafield.findall('unimarc:subfield', NAMESPACE)

            for subfield in subfields:
                xml_code = subfield.get('code')
                
                if xml_code in codes:
                    
                    if tag in ['710', '711', '712']:
                    # If there is a new 'a' code, start a new dictionary
                        if xml_code == 'a' and xml_code != 'b' and current_dict:
                        # Append the current dictionary to the result_list before starting a new one
                            result_list.append(current_dict)
                            current_dict = {}

                        current_dict[xml_code] = subfield.text.strip()
                        if xml_code == 'b':
                              all_b_values.append(subfield.text.strip())
                            
                    if tag in ['700', '701', '702']:
                      # If we encounter a new 'a' code, start a new dictionary
                        if xml_code == 'a' and current_dict:
                        # Append the current dictionary to the result_list before starting a new one
                            result_list.append(current_dict)
                            current_dict = {}
                        current_dict[xml_code] = subfield.text.strip()

    # Append the last dictionary if it has values
    if current_dict:
        result_list.append(current_dict)
        
        names_and_relator_codes = [
            {
            'name': f"{'' + item.get('b', '') if item.get('b', '') else ''} {item.get('a', '')}{', ' + item.get('f', '') if item.get('f', '') else ''}",
            'relator code': item.get('4', '') if item.get('4', '') else ''
            }
            for item in result_list
        ]
    
    if tag in ['700', '701', '702']:

        names_and_relator_codes = [
            {
            'name': f"{'' + item.get('b', '') if item.get('b', '') else ''} {item.get('a', '')}{', ' + item.get('f', '') if item.get('f', '') else ''}",
            'relator code': item.get('4', '') if item.get('4', '') else ''
            }
            for item in result_list
        ]
                                   
    elif tag in ['710', '711', '712']:
        # Join all 'b' values by space
        if len(all_b_values) > 0:
            b_values_str = '. '.join(all_b_values)
        else:
            b_values_str = ''
        names_and_relator_codes = [
            {
                'name': f"{item.get('a', '') if item.get('a', '') else ''}{'. ' + b_values_str if len(b_values_str) > 0 else ''}", 'relator code': item.get('4', '') if item.get('4', '') else ''
            } 
                for item in result_list
        ]

    if tag in ['700', '701', '702', '710', '711', '712']:
        names = []
        for item in names_and_relator_codes:
            if len(item["relator code"]) > 0:
                relator_code = get_relator_code_str(item["relator code"])
            
                names.append(f"{item['name']}, {relator_code}")
            else:
                names.append(f"{item['name']}" )
        
        result = " ; ".join(names)

    return result


def get_repeated_subfield_data(datafields, tag, codes, delimiter):
    
    result = {}
    
    all_a_language_values = []
    all_c_language_values = []
    
    publication_values = []
    first_publication_values = []
    second_publication_values = []
    
    pattern = r"[\x98\x9C\x88\x89«»<>?[\]\x80-\x9F\xa0\u200b\u200c\u200d\u2018\u2019\u02BC\xB4\u00BA\u00AA]+"

    for datafield in datafields:
        datafield_tag = datafield.get('tag')

        if datafield_tag == tag:
            subfields = datafield.findall('unimarc:subfield', NAMESPACE)
            count_publications = 0
            for subfield in subfields:
                xml_code = subfield.get('code')
                
                if xml_code in codes:

                    if tag == '101':
                        if xml_code == 'a':
                            all_a_language_values.append(get_language(subfield.text.strip()))
                        if xml_code == 'c':
                            all_c_language_values.append(get_language(subfield.text.strip()))
                    
                    if count_publications == 0:
                        count_publications += 1
                        if tag == '210':
                            if xml_code == 'a':
                                count_publications += 1
                                first_publication_values.append(subfield.text.strip())
                            elif xml_code == 'c':
                                first_publication_values.append(" : ")
                                first_publication_values.append(subfield.text.strip()) 

                    elif count_publications > 0:
                        if tag == '210':
                            if xml_code == 'a':
                                second_publication_values.append(" ; ")
                                second_publication_values.append(subfield.text.strip())
                            elif xml_code == 'c':
                                second_publication_values.append(" : ")
                                second_publication_values.append(subfield.text.strip())
    
    publication_values = first_publication_values + second_publication_values
    if tag == '210': 
        result = "".join(publication_values)
        result = re.sub(pattern, "", result)
                    
    if tag == '101': 
        result = {
                'línguas': delimiter.join(all_a_language_values),
                'línguas da obra original': delimiter.join(all_c_language_values)
        }

    return result

    
def get_cover(subfield):
    cover = ""    

    if re.search("purl", subfield.text.strip()):
        # time.sleep(1.5)
        bnd_link = extract_bnd_cover_link.get_bnd_link(subfield.text.strip())

        cover = extract_bnd_cover_link.get_cover(bnd_link, subfield)
                              
        if cover is not None:
            # get only the url's from the bndigital site
            if cover.find("bndigital") == -1:
                cover = f"https://bndigital.bnportugal.gov.pt/{cover}"
            else:
                cover = ""

    return cover

def remove_duplicates(input_list):
    # Use a set to track seen elements
    seen = set()
    # List comprehension to only include items not in 'seen'
    return [x for x in input_list if x not in seen and not seen.add(x)]


def get_data_from_non_repeatable_fields(doc_xml, object):
    count_purl = 0
    return_data = {}
    languages = {}
    publication = {}
    leader = ""
    return_data[object["name"]] = ""
    
    # names of the functions
    operations_map = {
        
        "get_subfield_with_specific_indicators": get_subfield_with_specific_indicators,
        "get_substring": get_substring,
        "cut_text_after_chars": cut_text_after_chars,
    }    
    
    datafields = doc_xml.findall(f'.//unimarc:{object["type"]}', NAMESPACE)  
    leader = doc_xml.findall('.//unimarc:leader', NAMESPACE)
    
    pattern = r"[\x98\x9C\x88\x89«»<>?[\]\x80-\x9F\xa0()']+"
    pattern_date = r"(-)+"
    # numbers_pattern = '([0-9]+)'

    # There is more than one link with field 856 and indicators 4 and 0. 
    if object["name"] == 'purl':
        count_purl += 1

    for datafield in datafields:
        
        tag = datafield.get('tag')
        indicators = [datafield.get('ind1'), datafield.get('ind2')]
        subfields = datafield.findall('unimarc:subfield', NAMESPACE)

        # To get the controlfields data which don't have subfields
        field_data = datafield.text
            
        # the leader type of field, doesn' have tag or subfields
        # This part of the code is only run if the object dictionnary has the leader defined   

        if field_data is not None:
            if return_data[object["name"]] is not None:
                
                return_data[object["name"]] = field_data.strip()
        else:
            return_data[object["name"]] = ""

        if object["type"] == "leader":
            return_data[object["name"]] = get_leader_data(leader)

        if object["tag"] == tag:
            object_codes_copy = object["codes"].copy()
            
            field_data = datafield.text
            
            # só está a extrair os códigos do primeiro 702
            codes = get_xml_codes(subfields, tag, object_codes_copy)
            codes = remove_duplicates(codes)
            
            for subfield in subfields:
                
                xml_codes = subfield.get('code')
            
                for xml_code in xml_codes:
                    for code in object["codes"]:
                        if code == xml_code:
                               
                        # The original language title is on the 304 field
                        # after "orig" and a dot or a colon
                            if subfield.text.strip() is not None:
                                field_data = re.sub(pattern, "", subfield.text.strip())
                                
                                # The wordpress fields don't support mmore than 200 chars
                                # if len(subfield.text.strip()) >= 200:
                                #     field_data = cut_string_with_more_than_200_chars(subfield.text.strip())
                                #     return_data[object["name"]] = field_data.strip()
                                    
                                if object["repeatable_field"] == 'yes':                                    
                                    subfields_dict = get_repeated_field_data(datafields, tag, codes, object["delimiter"])
                                    return_data[object["name"]] = subfields_dict

                                elif object["repeatable_subfield"] == 'yes':
                                    subfields_dict = get_repeated_subfield_data(datafields, tag, codes, object["delimiter"])
                                    if object["name"] == 'línguas':
                                        languages[object["name"]] = subfields_dict
                                    
                                    if object["name"] == 'publicação':
                                        return_data[object["name"]]  = subfields_dict
                                        
                                # Because the fields aren't repeatable
                                # But I want to use the same function of the repeatable fields
                                elif tag == '700' or tag == '710':

                                    return_data[object["name"]] = get_repeated_field_data(datafields, tag, object["codes"], "")
                                else:
                                    if return_data[object["name"]] is not None:
                                        return_data[object["name"]] = field_data.strip()
                                        
                            # Use the object operations key to call the respective functions
                            for operation, object_parameters in object["operations"].items():
                                if len(object_parameters) > 0:
                                    if operation in operations_map:
                                        
                                        # Apply the operation
                                        processed_data = operations_map[operation](subfield.text, object_parameters, indicators).strip()

                                        if field_data:
                                            field_data = processed_data
                                            
                                            if return_data[object["name"]] is not None:
                                                return_data[object["name"]] = field_data.strip()
                                                break
                        # The URL of the cover of the work is extracted from the site: bndigital.bnportugal.gov.pt
                        # It is not defined on the object dictionnary
                        
                        if object["name"] == 'purl':
                            get_capa = None
                            while get_capa is None and get_capa != 'PDF':
                                get_capa = get_cover(subfield)
                            if 'PDF' not in get_capa:
                                return_data["capa"] = get_capa
                            else:
                                return_data["capa"] = ''


                        # if object["name"] == 'purl':
                        #     get_capa = get_cover(subfield)
                        #     if get_capa is None:
                        #         get_capa = get_cover(subfield)
                                
                            
                        #     return_data["capa"] = get_capa
                            
 
                    # if field_data is not None:
                    #     field_data = re.sub(pattern, "", field_data)
                    #     if len(field_data) >= 200:
                            
                    #         field_data = cut_string_with_more_than_200_chars(field_data)
                    #         return_data[object["name"]] = field_data.strip()

            if return_data[object["name"]]:
                break

    if count_purl > 0 and len(return_data['purl']) == 0:
        return_data["capa"] = ""

    if len(languages) > 0:
        
        if object["name"] == 'línguas':
            for key, value in languages["línguas"].items():
                if key == 'línguas':
                    return_data["línguas"] = value.strip()
                if key == 'línguas da obra original':
                    return_data["línguas da obra original"] = value.strip()

    # if len(publication) > 0 and object["name"] == 'publicação':
    #     return_data["publicação"] = publication[object["name"]]

    #     return_data["línguas"] = 'teste'
    #     return_data["línguas da obra original"] = 'teste'

    # When it is the 1st edition, no data is written in the edition field
    # However it is a necessary information, so change none to "1.ª ed."
    if object["name"] == 'edição' and return_data["edição"] == '':
        return_data["edição"] = '1.ª ed.'
    
    if object["name"] == 'data de publicação' and len(return_data["data de publicação"]) > 0:
        date_size = len(return_data["data de publicação"])
        date_value = return_data["data de publicação"].replace("-", " ")
        try:
            int(date_value)
            
        except:
            date_value = ""
        else:
            date_value = int(date_value)
            # century = int(return_data["data de publicação"][:2]) + 1
            
            # The date value can have 2 chars, when there is no certainty regarding the decade and year
            # And 3, when there is no certainty regarding the year

            if date_size == 2:
                return_data["data de publicação"] = f"{str(date_value)}--"
            if date_size == 3:
                # decade = f"{return_data["data de publicação"][2]}0"
                return_data["data de publicação"] = f"{str(date_value)}-"


    return return_data
    

# Extract the fields values accordingly with the defined object fields and actions
def get_field_data(doc_xml, object):
    
    # if object["repeatable"] == "no":
    data = get_data_from_non_repeatable_fields(doc_xml, object)
    # else:
    #     data = get_data_from_non_repeatable_fields(doc_xml, object)

    
    return data


def get_fields_data_from_xml(doc_xml, objects):
    # Namespace
    # Got how it works from here: https://stackoverflow.com/questions/61551990/parse-xml-file-with-namespace-with-python
    # fields_types_data = {}
    
    # Repo record data extracted accordingly to the object fields and subfields
    record_data = {}
    
    aggregated_data = []
    
    for object in objects:
        xml_doc_field_values = get_field_data(doc_xml, object)
        aggregated_data.append(xml_doc_field_values)

        
        for field_name in xml_doc_field_values:
            record_data[field_name] = xml_doc_field_values[field_name]
    
    return record_data
        


f_report = open_file("report.csv", "a")

json_data_list = []
# for record in range(first_record, last_record, 1):
    # f_report.write(f'\n{record}')

with open('ncb.csv', mode='r', newline='') as file:

    while True:
        
        ncb=file.readline().strip()
        if not ncb:
            break        
        
        record_url = BASE_URL + str(ncb)

        try:
            response = urllib.request.urlopen(record_url, context=ctx)
            encoding = response.headers.get_content_charset(failobj='utf-8')
            doc_data = response.read().decode(encoding)
            # doc_data = urllib.request.urlopen(record_url, context=ctx).read().decode('utf-8')
    # Taken from: https://stackoverflow.com/questions/53755173/urllib-exception-handling-in-python3
        except Exception as e:
            print(e)
            save_error(f'Error trying to access/load page of the repo: {e}')

        try:
            doc_xml = ET.fromstring(doc_data)

        except ET.ParseError as e:
            save_error("Error when parsing xml: ", e)
        
        # Get the leader, controlfields and datafields data
        record_data = get_fields_data_from_xml(doc_xml, objects)
        # print(record_data)
        
        # json_data_list.append(record_data)

        
        # joined_author_data = join_data(record_data)

        
        # record_data.update(joined_author_data)

        
        # Generate links of the images to be downloaded
        
        if record_data["capa"] and 'PDF' not in record_data["capa"]:
            create_links.generate_resized_image_links(record_data["ncb"], record_data["capa"])

        # print(record_data)
        export_to_csv.to_csv(record_data)

        # convert_to_json.convert(json_data_list, JSON_FILE_PATH)


# Para já fica comentada a exportação para o Elasticsearch
# export_to_elasticsearch.export(INDEX, JSON_FILE_PATH)
    
    # with open('data.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(fields_types_data, json_file, ensure_ascii=False)


    # get_specific_field_data(fields_types_data, object)


file.close()
    