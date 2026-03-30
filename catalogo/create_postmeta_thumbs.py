import os
import mysql.connector
from datetime import datetime
import unicodedata
import re


def get_record_data(db, row):
    record = {}

    print("ROW: ", row)
    id_row = row['id']
    ncb = row['ncb']

    result = db.get_id_from_post(ncb)
    print("**************************", result)

    record["post_id"] = id_row
    record["meta_key"] = "_thumbnail_id"
    record["meta_value"] = result[0]['ID']

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

        record = get_record_data(db, row)
        print("######", record["meta_value"])
        db.insert_post_metadata(record["post_id"], record["meta_key"], str(record["meta_value"]))





	