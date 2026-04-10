import mysql.connector


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


def get_id(db, slugs_list):
    """Fetch term_ids from wp_terms based on slugs."""
    ids_list = []

    for slug in slugs_list:
        results = db.get_category_from_slug(slug)

        if results:
            ids_list.append(results[0]["term_id"])
            # print("*************", results[0] if results else None)

    return remove_duplicates(ids_list)


def get_ids_from_slugs(db, slugs_dict):
    """Generates all slug combinations and retrieves their corresponding term_ids."""
    slugs_list = []

    for _, slug in slugs_dict.items():
        parts = slug.split("-")
        slugs_list.extend(parts)  # Include each individual part

        for i in range(len(parts)):
            sub_slug = "-".join(parts[i:])  # All suffix combinations
            if sub_slug:
                slugs_list.append(sub_slug)

    return get_id(db, slugs_list)


def create_terms_relationships(db, collection):

    # Step 1: Read all records from source table
    records = db.get_csv_data(collection)

    for row in records:
        record_id = row["id"]
        print("RECORD ID:", record_id)

        category_ids = get_categories_ids(row)
        slugs_dict = {}

        for term_id in category_ids:
            result = db.get_slug_from_category(term_id)

            if result:
                slug = result[0]["slug"]
                print(slug)
                slugs_dict[term_id] = slug

        # Get taxonomy term IDs from all slugs and sub-slugs
        print(slugs_dict)
        taxonomy_ids = get_ids_from_slugs(db, slugs_dict)

        # Insert into wp_term_relationships
        for taxonomy_id in taxonomy_ids:
            db.insert_term_relationship(record_id, taxonomy_id, 0)

