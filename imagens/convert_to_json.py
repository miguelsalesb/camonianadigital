import json

# def convert(record_data):
#     index_part = {"index": {"_index": "camoniana", "_id": record_data["_id"]}}

    
#     # The rest of the dictionary
#     rest_of_data = {key: value for key, value in record_data.items() if key != "_id"}

#     with open('data.json', 'a', encoding='utf-8') as json_file:
#         json_file.write("\n")
#         json.dump(index_part, json_file, ensure_ascii=False)
#         json_file.write("\n")
#         json.dump(rest_of_data, json_file, ensure_ascii=False)   




# Remove the '_id' field and move it to a separate field for Elasticsearch _id
def transform_data_for_elasticsearch(data):
    transformed_data = []
    for record in data:
        transformed_record = {
            "id": record.pop('_id'),
            **record
        }
        transformed_data.append(transformed_record)
    return transformed_data

# Convert the data and write to JSON file
def write_data_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)



def convert(json_data_list, JSON_FILE_PATH):
    
    # Transform the data for Elasticsearch
    transformed_data = transform_data_for_elasticsearch(json_data_list)
    
    # Path to save the JSON file
    

    
    
    # Write the transformed data to JSON file
    write_data_to_json(transformed_data, JSON_FILE_PATH)
    
    print(f"Data successfully written to {JSON_FILE_PATH}")
