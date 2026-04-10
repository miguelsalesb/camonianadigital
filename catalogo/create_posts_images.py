import os
import mysql.connector
from datetime import datetime
import unicodedata
import re

# Get the current time
current_time = datetime.now()

# Format the current time as "yyyy-mm-dd HH:MM:SS"
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

BASE_URL = "https://camonianadigital.bnportugal.gov.pt"

def cut_string_with_more_than_200_chars(data):
    # The Wordpress title field only supports 200 characters
    field_data = f"{data[:197]}..."
    return field_data


def remove_diacritics(input_str):
	pattern = r"[^\w\s_-]"
	only_text = re.sub(pattern, "", input_str)
	
	nfkd_form = unicodedata.normalize('NFKD', only_text)
	print(only_text)
	
	return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_record_data(row, count, collection):
	
	record = {}
	# print("ROW: ", row)
	
	# To present the illustrator name
	 
	# fields to include in the post_content
	# if row["função autor secundário"] == "440":
	# 	illustrator = f"{row["nome autor secundário"]} {row["apelido autor secundário"]}"
	# else:
	# 	illustrator = ""

	ncb = row["ncb"]
	post_id = row["ID"]
	
	if collection == 'imagens' or collection == 'imagens2':
		volume = row["volume"]
		page_number = row['imagem']		
		record["post_title"] = f"{ncb}{volume}{page_number}"
		record["post_name"] = f"{ncb}{volume}{page_number}"
	elif collection == 'catalogo':
		record["post_title"] = ncb
		record["post_name"] = ncb
	# Truncar título com mais de 200 letras
	# No post_name retirar os diacriticos
	record["post_author"] = 1
	record["post_date"] = formatted_time
	record["post_date_gmt"] = formatted_time
	record["post_content"] = ""

	record["post_excerpt"] = ""
	record["post_status"] = "inherit"
	record["comment_status"] = "closed"
	record["ping_status"] = "closed"
	record["post_password"] = ""

	record["post_modified"] = formatted_time
	record["post_modified_gmt"] = formatted_time
	
	# if collection == 'catalogo':
	record["post_parent"] = post_id
	# elif collection == 'imagem1' or collection == 'imagem2':
	# 	record["post_parent"] = row['id']

	if collection == 'imagens' or collection == 'imagens2':

		record["guid"] = f"{BASE_URL}/wp-content/uploads/2025/capas/{ncb}{volume}{page_number}.jpg"
	elif collection == 'catalogo':
		record["guid"] = f"{BASE_URL}/wp-content/uploads/2025/capas/{ncb}.jpg"
	
	# record["guid"] = f"{SITE_URL}/wp-content/uploads/2025/capas/{ncb}.jpg"
	record["menu_order"] = 0
	record["post_type"] = "attachment"
	record["post_mime_type"] = "image/jpeg"
	record["comment_count"] = 0

	return record


def create_posts_images(db, collection):

	# to provide the post number to put at the end of the post URL
	count = 0
	record = {}

	results = db.get_collection_crossed_with_posts(collection)

	for row in results:
		count += 1

		record = get_record_data(row, count, collection)

		db.insert_post(record["post_author"], record["post_date"], record["post_date_gmt"], record["post_content"], record["post_title"], record["post_excerpt"], record["post_status"], record["comment_status"], record["ping_status"], record["post_password"], record["post_name"], '', '', record["post_modified"], record["post_modified_gmt"], '', record["post_parent"], record["guid"], record["menu_order"], record["post_type"], record["post_mime_type"], record["comment_count"])
		print("\nPOST IMAGE: ", record)





	