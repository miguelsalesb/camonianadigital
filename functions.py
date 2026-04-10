import os
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import re
import csv
from unidecode import unidecode


NAMESPACE = {'unimarc': 'info:lc/xmlns/marcxchange-v2'}
BASE_URL = "https://urn.bnportugal.gov.pt/ncb/unimarc/marcxchange?id="



def open_file(filename, mode):
        try:
            return open(filename, mode=mode)
        except:
            return None

# def create_report():
#     # Create a report file
#     if not os.path.exists('relatorio.csv'):    
#         return open('relatorio.csv', mode='a', encoding='utf-8')
        

f_report = open_file("report.csv", "a")
def save_error(e):
    f_report.write()
    f_report.flush()    


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
    # The Wordpress title field only supports 200 characters
    field_data = f"{data[:197]}..."
    return field_data


def get_subfield_with_specific_indicators(field_data, object_indicators, xml_doc_indicators):

    # In this situation, there is the need to get the field data
    # that has 'purl' in the URL, since only those are links to
    # the digital library
    
    data = ""    
    if 'purl' in field_data:
        field_data_list = []

        if int(object_indicators[0]) == int(xml_doc_indicators[0]) and int(object_indicators[1]) == int(xml_doc_indicators[1]):
            field_data_list.append(field_data)
            
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


def get_leader_data(leader_data):
    leader_str = ""
    for leader in leader_data:
        leader_str = get_material_type(leader.text)
        
    return leader_str



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
    with open('catalogo/lista-línguas.csv', mode='r', newline='') as file:
    
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
    result = {}
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

                        current_dict[xml_code] = subfield.text    
                        if xml_code == 'b':
                              all_b_values.append(subfield.text)                            
                            
                    if tag in ['700', '701', '702']:
                      # If we encounter a new 'a' code, start a new dictionary
                        if xml_code == 'a' and current_dict:
                        # Append the current dictionary to the result_list before starting a new one
                            result_list.append(current_dict)
                            current_dict = {}
                        current_dict[xml_code] = subfield.text    


      # Append the last dictionary if it has values
    if current_dict:
        result_list.append(current_dict)
        
        names_and_relator_codes = [
            {
            'name': f"{item.get('b', '')}{' ' + item.get('a', '') if item.get('a', '') else ''}{' ' + item.get('f', '') if item.get('f', '') else ''}",
            # 'relator code': item.get('4', '') if item.get('4', '') else ''
        
            }
            for item in result_list
        ]
    
    if tag in ['700', '701', '702']:

        names_and_relator_codes = [
            {
            'name': f"{item.get('b', '')}{' ' + item.get('a', '') if item.get('a', '') else ''}{', ' + item.get('f', '') if item.get('f', '') else ''}",
            # 'relator code': item.get('4', '') if item.get('4', '') else ''
            }
            for item in result_list
        ]
                                   
    # Removed the 712 field
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

    # Removed the 712 field
    if tag in ['700', '701', '702', '710', '711', '712']:
        names = []
        for item in names_and_relator_codes:
            if 'Portugal. ' in item["name"]:
                name = item['name'].replace("Portugal. ", "")
                names.append(name)
            else:
                names.append(item["name"])
        
        result = " ; ".join(names)

    return result


def get_repeated_subfield_data(datafields, tag, codes, delimiter):
    
    result = {}
    
    all_a_language_values = []
    all_c_language_values = []

    for datafield in datafields:
        datafield_tag = datafield.get('tag')

        if datafield_tag == tag:
            subfields = datafield.findall('unimarc:subfield', NAMESPACE)

            for subfield in subfields:
                xml_code = subfield.get('code')
                
                if xml_code in codes:

                    if tag == '101':
   
                        if xml_code == 'a':
                            
                            all_a_language_values.append(get_language(subfield.text))
                        if xml_code == 'c':
                            all_c_language_values.append(get_language(subfield.text))
    if tag == '101': 
        result = {
            
                'línguas': delimiter.join(all_a_language_values),
                'línguas da obra original': delimiter.join(all_c_language_values)
                   
        }

    return result

    
# def get_cover(subfield):
#     cover = ""    

#     if re.search("purl", subfield.text):
#         bnd_link = extract_bnd_cover_link.get_bnd_link(subfield.text)
#         cover = extract_bnd_cover_link.get_cover(bnd_link, subfield)
                                 
#         if cover is not None:
#             # get only the url's from the bndigital site
#             if cover.find("bndigital") == -1:
#                 cover = f"https://bndigital.bnportugal.gov.pt/{cover}"
#             else:
#                 cover = ""

#     return cover

def remove_duplicates(input_list):
    # Use a set to track seen elements
    seen = set()
    # List comprehension to only include items not in 'seen'
    return [x for x in input_list if x not in seen and not seen.add(x)]


def get_data_from_non_repeatable_fields(doc_xml, object):
    count_purl = 0
    return_data = {}
    languages = {}
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
    
    pattern = r"[\x98\x9C\x88\x89«»<>?\[\]]+"
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
                            if subfield.text is not None:
                                field_data = re.sub(pattern, "", subfield.text.strip())
                                # The wordpress fields don't support mmore than 200 chars
                                if len(subfield.text) > 200:
                                    field_data = cut_string_with_more_than_200_chars(subfield.text.strip())
                                
                                elif object["repeatable_field"] == 'yes':
                                    
                                    subfields_dict = get_repeated_field_data(datafields, tag, codes, object["delimiter"])
                                    return_data[object["name"]] = subfields_dict

                                elif object["repeatable_subfield"] == 'yes':
                                    
                                    subfields_dict = get_repeated_subfield_data(datafields, tag, codes, object["delimiter"])
                                    languages[object["name"]] = subfields_dict
                                
                                # Because the fields aren't repeatable
                                # But I want to use the same function of the repeatable fields
                                elif tag == '700' or tag == '710':
                                    
                                    return_data[object["name"]] = get_repeated_field_data(datafields, tag, object["codes"], "")
                                    
                                else:
                                    
                                    if return_data[object["name"]] is not None:
                                        return_data[object["name"]] = field_data
                                        
                            # Use the object operations key to call the respective functions
                            for operation, object_parameters in object["operations"].items():
                                if len(object_parameters) > 0:
                                    if operation in operations_map:
                                        
                                        # Apply the operation
                                        processed_data = operations_map[operation](subfield.text, object_parameters, indicators).strip()

                                        if field_data:
                                            field_data = processed_data
                                            
                                            if return_data[object["name"]] is not None:
                                                return_data[object["name"]] = field_data
                                                break
                        # The URL of the cover of the work is extracted from the site: bndigital.bnportugal.gov.pt
                        # It is not defined on the object dictionnary
                        
                        # if object["name"] == 'purl':
                        #     return_data["capa"] = get_cover(subfield)
 
                    if field_data is not None:
                        field_data = re.sub(pattern, "", field_data)
                        if len(field_data) > 200:
                            
                            field_data = cut_string_with_more_than_200_chars(field_data)
                            return_data[object["name"]] = field_data

            if return_data[object["name"]]:
                break

    if count_purl > 0 and len(return_data['purl']) == 0:
        return_data["capa"] = ""

    if len(languages) > 0:
        if object["name"] == 'línguas':
            for key, value in languages["línguas"].items():
                if key == 'línguas':
                    # value[0:2] since there are cases that have more than 3 chars
                    return_data["línguas"] = value
                if key == 'línguas da obra original':
                    return_data["línguas da obra original"] = value




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
       
    
   # Because there are empty records
    # if len(return_data) > 0:
        # print(return_data)
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
        

def convert_to_century(date):
    # Fix incomplete dates
    if date.endswith("--"):
        date = date.replace("--", "01")
    elif date.endswith("-"):
        date = date.replace("-", "1")

    # Convert to integer
    try:
        date_int = int(date)
    except ValueError:
        return "Data inválida"


    # Determine century
    if 1501 <= date_int <= 1600:
        return "Século (1) XVI"    
    if 1601 <= date_int <= 1700:
        return "Século (2) XVII"
    elif 1701 <= date_int <= 1800:
        return "Século (3) XVIII"
    elif 1801 <= date_int <= 1900:
        return "Século (4) XIX"
    elif 1901 <= date_int <= 2000:
        return "Século (5) XX"
    elif date_int >= 2001:
        return "Século (6) XXI"
    else:
        return "Data fora do intervalo"


def get_slug(field_value, key):

    category_size = len(field_value)
    slugs_text = ""

    if re.search(" ", field_value):
        slug = unidecode(field_value.lower().strip().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", ""))
    else:
        slug = unidecode(field_value.lower().strip().replace("(", "").replace(")", "").replace(",", "").replace(".", ""))
                            
    # Change before writing the slugs 
    # to: category, author, edition, language, etc.
    if 'autor' in key:
        slugs_text = slug + "_tag"
    elif 'tipo de material' in key:
        slugs_text = slug + "_pa_tipo-de-material"
    elif 'língua' in key:
        slugs_text = slug + "_pa_lingua"
    elif 'seculo de publicação' in key:
        slug_converted_to_century = convert_to_century(slug)
        slug = unidecode(slug_converted_to_century.lower().strip().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", ""))
        slugs_text = slug + "_pa_seculo"
    elif 'data de publicação' in key:
        slugs_text = slug + "_pa_ano"
        # century = convert_to_century(slug)
        # slugs_text = century + "_pa_sec"
    # elif 'edição' in key:
    #     slugs_text = slug + "pa_edicao"
        
    return slugs_text