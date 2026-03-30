import os
import mysql.connector
from datetime import datetime
import unicodedata
import re


def create_csv_with_posts_and_images(db, id):

  file = open('catalogo/post-image-map.csv', mode='w', encoding='utf-8')

  result = db.get_id_and_post_parent(id)
  print("result: ", result)

  for row in result:
      print(row['id'], row['post_parent'])
      file.write(f"{row['id']};{row['post_parent']}\n")
      file.flush()

  file.close()
