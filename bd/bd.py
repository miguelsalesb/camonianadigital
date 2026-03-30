import mariadb
import sys

class DatabaseManager:
    def __init__(self, host, port, user, password):
        """Initialize with credentials only — no database selected yet."""
        try:
            self.conn = mariadb.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            self.conn.autocommit = False
            self.cursors = {}  # One cursor per database
            print("Successfully connected to MariaDB.")
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")
            sys.exit(1)

    def use_database(self, database):
        """Select a database and create a dedicated cursor for it."""
        try:
            if database not in self.cursors:
                self.conn.cursor().execute(f"USE `{database}`")
                self.cursors[database] = self.conn.cursor()
                print(f"Now using database: {database}")
        except mariadb.Error as e:
            print(f"Error selecting database '{database}': {e}")

    def get_cursor(self, database):
        """Retrieve the cursor for a given database."""
        if database not in self.cursors:
            self.use_database(database)
        return self.cursors[database]
    
    def get_dictionnary_cursor(self, database, dictionary=False):
        """Retrieve the cursor for a given database."""
        if database not in self.cursors:
            self.use_database(database)
        
        if dictionary:
            return self.cursors[database].connection.cursor(dictionary=True)
        
        return self.cursors[database]


    def commit(self):
        """Commit the current transaction (shared across all databases)."""
        self.conn.commit()

    def rollback(self):
        """Roll back the current transaction."""
        self.conn.rollback()

    def close(self):
        """Close all cursors and the connection."""
        for cursor in self.cursors.values():
            cursor.close()
        self.conn.close()
        print("Database connection closed.")

    # --- Example functions specifying which database to use ---

    def get_categories(self):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT * FROM wordpress.wp_terms")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching categories: {e}")
            return []
  
        
    def get_temp_categories(self, value):
        cursor = self.get_cursor("wordpress_temp")
        try:
            cursor.execute("SELECT term FROM wordpress_temp.all_categories WHERE term = ?", (value,))
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching temp category: {e}")
            return []

    def get_category_from_temp_categories(self, value):
        cursor = self.get_cursor("wordpress_temp")
        try:
            cursor.execute("SELECT * FROM wordpress_temp.all_categories WHERE taxonomy LIKE ?", ("%" + value + "%",))
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching temp taxonomy: {e}")
            return [] 

    def get_category(self, value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT * FROM wordpress.wp_terms WHERE name = ?", (value,))
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching category: {e}")
            return []
        
    def get_slugs(self, value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT * FROM wordpress.wp_terms WHERE slug = ?", (value,))
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching slug: {e}")
            return []
        
    def get_slug(self, value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT slug FROM wordpress.wp_terms WHERE slug = ?", (value,))
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching slug: {e}")
            return []

    def get_slug_from_category(self, value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT slug FROM wordpress.wp_terms WHERE term_id = ?", (value,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except mariadb.Error as e:
            print(f"Error fetching slug: {e}")
            return []


    def get_category_from_slug(self, value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute("SELECT term_id FROM wordpress.wp_terms WHERE slug = ?", (value,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except mariadb.Error as e:
            print(f"Error fetching slug: {e}")
            return []


    def get_csv_data(self, collection):
        cursor = self.get_dictionnary_cursor("csv_data", dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM csv_data.{collection} WHERE ncb > 0")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []
        

    def get_collection_crossed_with_posts(self, collection):
        cursor = self.get_dictionnary_cursor("csv_data", dictionary=True)
        try:
            cursor.execute(f"SELECT * FROM csv_data.{collection} c JOIN wordpress.wp_posts w ON c.id = w.ID WHERE c.ncb > 0")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []


    def get_id_and_ncb(self, collection):
        cursor = self.get_dictionnary_cursor("csv_data", dictionary=True)
        try:
            cursor.execute(f"SELECT id, ncb FROM csv_data.{collection} ")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []


    def get_id_from_csv_data(self, collection, ncb):
        cursor = self.get_dictionnary_cursor("csv_data", dictionary=True)
        try:
            cursor.execute(f"SELECT id FROM csv_data.{collection} WHERE ncb = {ncb}")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []


    def get_id_from_post(self, post_title):
        cursor = self.get_dictionnary_cursor("wordpress", dictionary=True)
        try:
            cursor.execute(f"SELECT ID FROM wordpress.wp_posts WHERE post_title = {post_title}")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []


    def get_posts_with_attachment_type(self, collection):
        cursor = self.get_dictionnary_cursor("wordpress", dictionary=True)
        if collection == 'catalogo':
            try:
                cursor.execute(f"SELECT ID, post_title FROM wordpress.wp_posts WHERE post_type = 'attachment'")
                return cursor.fetchall()
            except mariadb.Error as e:
                print(f"Error fetching catalogo: {e}")
                return []
        elif collection == 'imagens':
            try:
                cursor.execute(f"SELECT w.ID, w.post_title, c.volume, c.imagem FROM wordpress.wp_posts w JOIN csv_data.{collection} c ON w.ID = c.id WHERE w.post_type = 'attachment'")
                return cursor.fetchall()
            except mariadb.Error as e:
                print(f"Error fetching catalogo: {e}")
                return []            


    def get_postmeta(self, post_id):
        cursor = self.get_dictionnary_cursor("wordpress", dictionary=True)
    
        try:
            cursor.execute(f"SELECT * FROM wordpress.wp_postmeta WHERE post_id = {post_id} and meta_key = '_wp_attached_file'")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []
    


    def get_id_and_post_parent(self, id):
        cursor = self.get_dictionnary_cursor("wordpress", dictionary=True)
        try:
            cursor.execute(f"SELECT id, post_parent FROM wordpress.wp_posts WHERE ID > {id} AND post_parent > 0")
            return cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error fetching catalogo: {e}")
            return []


    def insert_category(self, name, slug):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(
                "INSERT INTO wordpress.wp_terms (name, slug) VALUES (?, ?)",
                (name, slug)
            )
            self.commit()
            print(f"Inserted category: {name}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting category, rolled back: {e}")

    def insert_taxonomy(self, term_id, taxonomy, description, parent, count):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(
                "INSERT INTO wordpress.wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (?, ?, ?, ?, ?)",
                (term_id, taxonomy, description, parent, count)
            )
            self.commit()
            print(f"Inserted category: {taxonomy}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting category, rolled back: {e}")               
    
   
    def insert_temp_category(self, ncb, term, slug, taxonomy):
        cursor = self.get_cursor("wordpress_temp")
        try:
            cursor.execute(
                "INSERT INTO wordpress_temp.all_categories (ncb, term, slug, taxonomy) VALUES (?, ?, ?, ?)",
                (ncb, term, slug, taxonomy)
            )
            self.commit()
            print(f"Inserted category: {term}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting temp_category, rolled back: {e}")


    def insert_term_relationship(self, object_id, term_taxonomy_id, term_order):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(
                "INSERT INTO wordpress.wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)",
                (object_id, term_taxonomy_id, term_order)
            )
            self.commit()
            print(f"Inserted term_relationship: {term_taxonomy_id}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting category, rolled back: {e}")


    def auto_increment(self, database, table, id):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(f"ALTER TABLE {database}.{table} AUTO_INCREMENT = {id}")
            self.commit()
            print(f"ID starts at: {id}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error changing AUTO_INCREMENT, rolled back: {e}")   


    def delete(self, database, table, id):
        cursor = self.get_cursor("wordpress")
        if table == 'wp_posts':
            field = 'ID'
        elif table == 'wp_postmeta':
            field = 'meta_id'
        elif table == 'wp_term_relationships':
            field = 'object_id'
        elif table == 'wp_terms':
            field = 'term_id'
        elif table == 'all_categories':
            field = 'id'
        elif table == 'wp_term_taxonomy':
            field = 'term_taxonomy_id'
        elif table == 'wp_postmeta':
            field = 'meta_id'                         

        try:
            cursor.execute(f"DELETE FROM {database}.{table} WHERE {field} >= {id}")
            self.commit()
            print(f"ID starts at: {id}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error DELETING, rolled back: {e}")


    def insert_post(self, post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(
                "INSERT INTO wordpress.wp_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_password, post_name, to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent, guid, menu_order, post_type, post_mime_type, comment_count)
            )
            self.commit()
            print(f"Inserted post: {post_title}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting category, rolled back: {e}")


    def insert_post_metadata(self, post_id, meta_key, meta_value):
        cursor = self.get_cursor("wordpress")
        try:
            cursor.execute(
                "INSERT INTO wordpress.wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)",
                (post_id, meta_key, meta_value)
            )
            self.commit()
            print(f"Inserted post_meta: {post_id}")
        except mariadb.Error as e:
            self.rollback()
            print(f"Error inserting category, rolled back: {e}")