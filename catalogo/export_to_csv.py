import csv
import ast
import re

file = open('info-bibliografica.csv', mode='w', encoding='utf-8')

header = 'ncb|purl|capa|tipo de material|língua|língua da obra original|título|subtítulo|título original|edição|publicação|data da publicação|data da publicação2|dimensões|autor|autor - organização|co-autores|autores secundários|co-autores - organizações|autores secundários - organizações|cota|coleção|id persistente|acesso|notas gerais|notas título|notas conteúdo|sumário|título uniforme|título colectivo uniforme'

file.write(header)
file.flush()



def extract_value(value):
    # If value is already a type like int, str, etc., return it as-is
    if isinstance(value, (int, float, str)):
        return value
    
    try:
        # Convert string to tuple and extract the first element
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # Return the value as-is if it's not a tuple-like string
        return value



def flatten_string(data_list):
    flattened_string = '|'.join([item[0] for item in data_list])

    return flattened_string



def to_csv(data):
    print(data)
    flattened_data = {}
        

    for key, value in data.items():
        print("#####################", key, value)
        # # if isinstance(value, dict):
        # print("****************************")
        #     # Se o valor é um dicionário com 'autores' e 'códigos de função'
        # if 'autores' in value:
        #     flattened_data[key + '_autores'] = value['autores']
        #         # flattened_data[key + '_codigos_funcao'] = value['códigos de função']
        # if key == 'línguas' in value:
        #     flattened_data[key + '_línguas'] = value['línguas']

        if key == "data de publicação":
            if value.endswith("--"):
                value = value.replace("--", "01")
            elif value.endswith("-"):
                value = value.replace("-", "0")        
            flattened_data["data de publicação2"] = value


        # else:
        flattened_data[key] = value

    # If there is no field 101 values add two empty columns data
    if len(flattened_data["línguas"]) == 0:
        flattened_data["línguas"] = "|"
    # if not flattened_data["línguas da obra original"]:    
        flattened_data["línguas da obra original"] = ""


    
    
    # if len(flattened_data["línguas"]) == 0:
        
    #     flattened_data["línguas da obra original"] = ""
    
    # except:
        # flattened_data["língua da obra original"] = "língua da obra original"
    # Converter valores para string, substituindo None por string vazia
    flattened_string = "|".join(str(value) if value is not None else "" for value in flattened_data.values())
    
    
    file.write(f"\n{flattened_string}")
    file.flush()

# def to_csv(data):
#     for key, value in data.items():
#         if len(value) > 0:
#             pass
            # print("\n", value)