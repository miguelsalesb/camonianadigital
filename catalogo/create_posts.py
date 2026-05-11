import os
import mysql.connector
from datetime import datetime
import unicodedata
import re

# Get the current time
current_time = datetime.now()

# Format the current time as "yyyy-mm-dd HH:MM:SS"
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

f_tit = open("errors_creating-posts.csv", "w", encoding="utf-8")

# CHANGE LATER TO: https://camonianadigital.bnportugal.gov.pt
BASE_URL = "https://camonianadigital.bnportugal.gov.pt"


def cut_string_with_more_than_100_chars(data):
	# Title should only have the most 100 chars
	field_data = data[:100]
	
	# To remove the last word if it is not complete
	text_before_last_space = field_data.rfind(" ")
	
	titl = field_data[:text_before_last_space]

	# To check if the last word is a article 
	# or some other word that doesn't 
	# add meaning and remove it
	data_list = titl.split(" ")

	to_check = {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'des', 'da', 'das', 'do', 'dos'}
	
	while data_list and data_list[-1].lower() in to_check:
		data_list.pop()

	title = " ".join(data_list)
    # The Wordpress title field supports a maximum of 200 characters. 100 is better

	return title


def remove_diacritics(input_str):
	pattern = r"[^\w\s_&-yyy]"
	only_text = re.sub(pattern, "", input_str)
	
	nfkd_form = unicodedata.normalize('NFKD', only_text)
	print(only_text)
	
	return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_record_data(row, collection):
	record = {}
	# print("ROW********************************:", row)
	# To present the illustrator name
	 
	# fields to include in the post_content
	# if row["função autor secundário"] == "440":
	# 	illustrator = f"{row["nome autor secundário"]} {row["apelido autor secundário"]}"
	# else:
	# 	illustrator = ""

	language = row["língua"]

	# It is not the cover data. If it doesn't exist then there is no cover
	capa = row["capa"]

	ncb = row["ncb"]
	catalogue_record = f"http://id.bnportugal.gov.pt/bib/catbnp/{ncb}"
	# cover = f"<!-- wp:image {{'className':'size-full'}} --><figure class='wp-block-image size-full'><img src='{SITE_URL}/wp-content/uploads/2025/capas/{ncb}.jpg' alt='Imagem da capa da obra'/></figure><!-- /wp:image -->"
	# cover = f"<figure><img src='wp-content/uploads/2025/capas{ncb}' alt='Imagem da capa'/></figure>"
	edition = row["edição"]
	publication = row["publicação"]
	# editor = row["editor"]
	date_of_publication = row["data da publicação"]
	number_of_pages = row["dimensões"]
	author = f"{row["autor"]}"
	author_organization = f"{row["autor - organização"]}"
	co_author = f"{row["co-autores"]}"
	co_author_organization = f"{row["co-autores - organizações"]}"
	other_author = f"{row["autores secundários"]}"
	other_author_organization = f"{row["autores secundários - organizações"]}"
	purl = row["purl"]
	# number_of_pages = row["número de páginas"]
	material_type = row["tipo de material"]
	title = row["título"]
	subtitle = row["subtítulo"]
	access = row["acesso"]




	# Some titles and subtitles have two spaces between words and
	#  that causes errors in the post_name, so the two spaces have to be converted to one
	# more_info = ""
	# if row["notas gerais"]:
	# 	more_info += row["notas gerais"] + "\n"
	# if row["notas título"]:
	# 	more_info += row["notas título"] + "\n"
	# if row["notas conteúdo"]:
	# 	more_info += row["notas conteúdo"] + "\n"
	# if row["sumário"]:
	# 	more_info += row["sumário"] + "\n"
	# if row["título uniforme"]:
	# 	more_info += row["título uniforme"] + "\n"
	# if row["título colectivo uniforme"]:
	# 	more_info += row["título colectivo uniforme"]				

	# Post_name has to have the ncb to distinguish from the works that have the same title
	# if title != '' and subtitle != '':
	# 	post_name = f"{title}-{subtitle}"
	# elif title != '':
	# 	post_name = title
	# else:
	# 	post_name = title

	post_name = title
	
	# tipo de material	língua	língua da obra original	título	subtítulo	título original	edição	lugar da publicação	data da publicação	editor	nome	apelido	nome autor secundário	apelido autor secundário	função autor secundário	cota	purl	capa	coleção	id persistente	nome completo

	if '  ' in post_name:
		f_tit.write(f"O título tem dois espaços;{ncb};{post_name}\n")
		f_tit.flush()
	if len(post_name) >= 100:
		post_name = cut_string_with_more_than_100_chars(post_name)
		post_name = post_name.lower().rstrip().replace(" ", "-").replace("  ", "").replace(",", "").replace(".", "").replace(";", "")
		
	post_name = remove_diacritics(post_name.lower().rstrip().replace(" ", "-").replace("  ", "").replace(",", "").replace(".", "").replace("&","").replace("---", "-").replace("--", "-").replace("...", "").replace(";", ""))
	
	post_data_to_add = ''
	
	if collection == 'imagens':
		# folder = row["pasta"]
		volume = row["volume"]
		page_number = row['imagem']
		page_url = row['url_pagina']
		post_name = f"{post_name}-{ncb}{volume}{page_number}"
		post_data_to_add = (
    (f"<div class='book-field'><strong>Número da página: </strong>{page_number}</div>" if page_number != '' else '') +
    (f"<div class='book-field'><strong>Link para a página da imagem: </strong><a href='{page_url}'>{page_url}</a></div>" if page_url != '' else '')
)	
	if author or co_author or author_organization or co_author_organization:
		others = ( 
			(f"<div class='book-field'><strong>Outros: </strong>{other_author} ; {other_author_organization}</div>" if other_author != '' and other_author_organization != '' else '') +
			(f"<div class='book-field'><strong>Outros: </strong>{other_author}</div>" if other_author != '' and other_author_organization == '' else '') +
			(f"<div class='book-field'><strong>Outros: </strong>{other_author_organization}</div>" if other_author_organization != '' and other_author == '' else '')
		)			
	else:
		others = ( 
			(f"<div class='book-field'><strong>Autores: </strong>{other_author} ; {other_author_organization}</div>" if other_author != '' and other_author_organization != '' else '') +
			(f"<div class='book-field'><strong>Autores: </strong>{other_author}</div>" if other_author != '' and other_author_organization == '' else '') +
			(f"<div class='book-field'><strong>Autores: </strong>{other_author_organization}</div>" if other_author_organization != '' and other_author == '' else '')
		)	

	if collection == 'catalogo':
		post_name = f"{post_name}-{ncb}"

	# Post name has to be different because it is part of the url and
	# "volume-image number" dos the job
	# elif collection == 'imagens':
		

	# Truncar título com mais de 200 letras
	# No post_name retirar os diacriticos
	# title_without_diacritics = remove_diacritics(row["título"].lower().rstrip().replace(" ", "-").replace("  ", " "))
	# subtitle_without_diacritics = remove_diacritics(row["subtítulo"].lower().rstrip().replace(" ", "-").replace("  ", " "))

	record["post_author"] = 1
	record["post_date"] = formatted_time
	record["post_date_gmt"] = formatted_time
	
	# record["post_content"] = more_info - Not needed
	record["post_content"] = ""
	
	# The title has the date if it exists
	if subtitle != "" and date_of_publication != "":
		record["post_title"] = f"{title}: {subtitle} ({date_of_publication})"
	elif subtitle != "" and date_of_publication == "":
		record["post_title"] = f"{title}: {subtitle}"
	elif subtitle == "" and date_of_publication != "":
		record["post_title"] = f"{title} ({date_of_publication})"



	record["post_excerpt"] =  	(
							(f"<div class='book-container'>") +
          					# (f"<div class='book-cover'><a href='{purl if purl != '' else ''}' target='_blank'>{cover if capa != '' else ''}</a></div>") +
							(f"<div class='book-info'>") +
							# PAGE INFORMATION
							# WORK INFORMATION							
							(f"<div class='book-field'><strong>Autor: </strong>{author}</div>" if author != '' else f"<div class='book-field'><strong>Autor: </strong>{author_organization}</div>" if author_organization != '' else '') +
							(f"<div class='book-field'><strong>Co-autores: </strong>{co_author} ; {co_author_organization}</div>" if co_author != '' and co_author_organization != '' else '') +
							(f"<div class='book-field'><strong>Co-autores: </strong>{co_author}</div>" if co_author != '' and co_author_organization == '' else '') +
							(f"<div class='book-field'><strong>Co-autores: </strong>{co_author_organization}</div>" if co_author_organization != '' and co_author == '' else '') +
							# (f"<div class='book-field'><strong>Outros: </strong>{other_author} ; {other_author_organization}</div>" if other_author != '' and other_author_organization != '' else '') +
							# (f"<div class='book-field'><strong>Outros: </strong>{other_author}</div>" if other_author != '' and other_author_organization == '' else '') +
							# (f"<div class='book-field'><strong>Outros: </strong>{other_author_organization}</div>" if other_author_organization != '' and other_author == '' else '') +
							others +
							(f"<div class='book-field'><strong>Publicação: </strong>" if publication != '' or date_of_publication != '' else '') +
							(f"{publication}" if publication != '' else '') +
							# (f"{place_of_publication}" if place_of_publication != '' else '') +
							# (f" : {editor}" if editor != '' else f"{editor}" if editor != '' and place_of_publication != '' else '') +
							# (f", {date_of_publication}" if date_of_publication != '' and editor != '' else f"{date_of_publication}") +
							(f", {date_of_publication}" if date_of_publication != '' and publication != '' else '' ) +
							(f"{date_of_publication}" if date_of_publication != '' and publication == '' else '' ) +							
							(f"</div>" if publication != '' or date_of_publication != '' else '') +
							(f"<div class='book-field'><strong>Língua: </strong>{language}</div>" if language != '' else '') +
							(f"<div class='book-field'><strong>Edição: </strong>{edition}</div>" if edition != '' else '') +							
							(f"<div class='book-field'><strong>Descrição física: </strong>{number_of_pages}</div>" if number_of_pages != '' else '') +
							(f"<div class='book-field'><strong>Registo no catálogo: </strong>{catalogue_record}</div>" if catalogue_record != '' else '') +
							(f"<div class='book-field'><strong>Digitalização integral: </strong><a href='{purl}' target='_blank'>{purl}</a></div>" if purl != '' else '') +
							(f"<div class='book-field'><strong>Tipo: </strong>{material_type}</div>" if material_type != '' else '') +
							(f"<div class='book-field'><strong class='acesso'>Acesso: </strong>{access} (acessível apenas na rede interna da BNP)</div>" if access != '' and access == 'Interno' else '') +
							(f"<div class='book-field'><strong>Acesso: </strong>{access}</div>" if access != '' and access == 'Livre' else '') +
							post_data_to_add +
							(f"</div>") +
							(f"</div>")
	)
	record["post_status"] = "publish"
	record["comment_status"] = "closed"
	record["ping_status"] = "closed"
	record["post_password"] = ""
	record["post_name"] = post_name
	record["post_modified"] = formatted_time
	record["post_modified_gmt"] = formatted_time
	record["post_parent"] = 0
	record["guid"] = f"{BASE_URL}/obra/{post_name}"
	record["menu_order"] = 0
	record["post_type"] = "product"
	record["comment_count"] = 0

	return record



def create_posts(db, id, collection):

	# to provide the post number to put at the end of the post URL
	count = 0
	record = {}


	if id > 0 and collection == 'catalogo':
		db.delete('wordpress', 'wp_posts', id)
		db.auto_increment('wordpress', 'wp_posts', id)    

	
	records = db.get_csv_data(collection)

	for row in records:
		count += 1
		record = get_record_data(row, collection)
		# val = (record["post_author"], record["post_date"], record["post_date_gmt"], record["post_content"], record["post_title"], record["post_excerpt"], record["post_status"], record["comment_status"], record["ping_status"], record["post_password"], record["post_name"], '', '', record["post_modified"], record["post_modified_gmt"], '', record["post_parent"], record["guid"], record["menu_order"], record["post_type"], '', record["comment_count"])
		db.insert_post(record["post_author"], record["post_date"], record["post_date_gmt"], record["post_content"], record["post_title"], record["post_excerpt"], record["post_status"], record["comment_status"], record["ping_status"], record["post_password"], record["post_name"], '', '', record["post_modified"], record["post_modified_gmt"], '', record["post_parent"], record["guid"], record["menu_order"], record["post_type"], '', record["comment_count"])
		print("\nPOST: ", count, record)
		


#(post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_password,post_name,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_parent,guid,menu_order,post_type,post_mime_type,comment_count)









	