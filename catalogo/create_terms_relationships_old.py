import mysql.connector

# --- Configuration ---
TABLE_READ_1 = 'catalogo'
TABLE_READ_2 = 'wp_terms'
TABLE_WRITE_1 = 'wp_term_relationships'

# --- Database Connections ---
read_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="csv_data"
)

wordpress_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="wordpress"
)

# --- Cursors ---
my_cursor = read_db.cursor(dictionary=True)
wp_cursor = wordpress_db.cursor(dictionary=True)

# --- Utility Functions ---

def get_categories_ids(row):
    """Extracts category term_ids from columns like 'Categoria-1' to 'Categoria-36'."""
    ids = []
    for i in range(36):  # total number of category columns
        val = row.get(f"Categoria-{i}", "")
        if val:
            ids.append(val.split("|")[-1])  # Get the last element (term_id)
    return ids


def remove_duplicates(ids_list):
    """Remove duplicates while preserving order."""
    seen = set()
    return [x for x in ids_list if not (x in seen or seen.add(x))]


def get_id(slugs_list):
    """Fetch term_ids from wp_terms based on slugs."""
    ids_list = []

    local_cursor = wordpress_db.cursor(dictionary=True)

    for slug in slugs_list:
        query = f"SELECT term_id FROM {TABLE_READ_2} WHERE slug = %s"

        try:
            local_cursor.execute(query, (slug,))
            # Force full fetch to avoid unread results issue
            results = local_cursor.fetchall()
            if results:
                ids_list.append(results[0]["term_id"])
            print("*************", results[0] if results else None)

        except mysql.connector.errors.InternalError as e:
            print(f"InternalError on slug {slug}: {e}")
            # Try to consume/clear result to recover the connection
            try:
                while local_cursor.fetchone():
                    pass
            except:
                pass
            continue

    try:
        local_cursor.fetchall()  # Final safety clear
    except:
        pass

    local_cursor.close()
    return remove_duplicates(ids_list)


def get_ids_from_slugs(slugs_dict):
    """Generates all slug combinations and retrieves their corresponding term_ids."""
    slugs_list = []

    for _, slug in slugs_dict.items():
        parts = slug.split("-")
        slugs_list.extend(parts)  # Include each individual part

        for i in range(len(parts)):
            sub_slug = "-".join(parts[i:])  # All suffix combinations
            if sub_slug:
                slugs_list.append(sub_slug)

    return get_id(slugs_list)


# --- Main Process ---

# Step 1: Read all records from source table
sql_search_1 = f"SELECT * FROM {TABLE_READ_1} WHERE id > 0"
my_cursor.execute(sql_search_1)
records = my_cursor.fetchall()

for row in records:
    record_id = row["id"]
    print("RECORD ID:", record_id)

    category_ids = get_categories_ids(row)
    slugs_dict = {}

    for term_id in category_ids:
        sql_slug = f"SELECT slug FROM {TABLE_READ_2} WHERE term_id = %s"
        wp_cursor.execute(sql_slug, (term_id,))
        result = wp_cursor.fetchone()
        print("444444444444444444444444444444", result)

        if result:
            slug = result["slug"]
            
            slugs_dict[term_id] = slug
    print("33333333333333333333333333333333", slugs_dict)
    # Get taxonomy term IDs from all slugs and sub-slugs
    taxonomy_ids = get_ids_from_slugs(slugs_dict)
    print("##############", taxonomy_ids)

    # Insert into wp_term_relationships
    sql_insert = f"INSERT INTO {TABLE_WRITE_1} (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)"
    for taxonomy_id in taxonomy_ids:
        pass
        # wp_cursor.execute(sql_insert, (record_id, taxonomy_id, 0))
        # wordpress_db.commit()

# --- Cleanup ---
my_cursor.close()
wp_cursor.close()
read_db.close()
wordpress_db.close()
