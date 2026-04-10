import os
import mysql.connector
from datetime import datetime
import unicodedata
import re


def get_record_data(db, row, collection):
    record = {}

    id_row = row['id']
    if collection == 'catalogo':
        ncb = row['ncb']
    elif collection == 'imagens':
        ncb = row['ncb2']
    

    result = db.get_id_from_post(ncb)
    print("POSTMETA: ", result)

    record["post_id"] = id_row
    record["meta_key"] = "_thumbnail_id"
    # if collection == 'catalogo':
    record["meta_value"] = result[0]['ID']
    # elif collection == 'imagens' or collection == 'imagens2':
    #     record["meta_value"] = result[0]['ncb2']
    return record



def create_postmeta_thumbs(db, id, collection):

    # to provide the post number to put at the end of the post URL
    record = {}

    if int(id) > 0 and collection == 'catalogo':
        db.delete('wordpress', 'wp_postmeta', id)
        db.auto_increment('wordpress', 'wp_postmeta', id)    

    result = db.get_id_and_ncb(collection)

    for row in result:
        print(row["id"])

        record = get_record_data(db, row, collection)
        print("META VALUE: ", record["meta_value"])
        db.insert_post_metadata(record["post_id"], record["meta_key"], str(record["meta_value"]))





	