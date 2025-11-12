import sqlite3
from settings import Settings


class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(Settings.DATABASE_PATH)
            # self.create_tables()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def __del__(self):
        if self.conn:
            self.conn.close()

    def subcategories(self, guid):
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*)  FROM category  WHERE parent_id = ?''', (guid,))
        return cursor.fetchone()[0]

    def get_categories_with_products_hierarchy(self, parent_guid=None):
        """
        Возвращает иерархию категорий, в которых есть товары (прямо или в дочерних)
        :param parent_guid: если None - корневые категории с товарами,
                           если указан - дочерние категории с товарами для этого родителя
        :return: список категорий (guid, name, parent)
        """
        try:
            self.cursor = self.conn.cursor()
            if parent_guid is None:
                # Корневые категории, в которых есть товары (прямо или в дочерних)
                self.cursor.execute("""
                    WITH RECURSIVE category_tree AS (
                        -- Базовый случай: все категории, в которых есть товары
                        SELECT DISTINCT c.category_id, c.name, c.parent_id, c.extension
                        FROM category c
                        INNER JOIN product p ON p.category = c.category_id

                        UNION

                        -- Рекурсивный случай: родительские категории
                        SELECT c.category_id, c.name, c.parent_id, c.extension
                        FROM category c
                        INNER JOIN category_tree ct ON c.category_id = ct.parent_id
                    )
                    SELECT DISTINCT category_id, name, parent_id, extension
                    FROM category_tree 
                    WHERE parent_id IS NULL
                    ORDER BY name
                """)
            else:
                # Дочерние категории с товарами для указанного родителя
                self.cursor.execute("""
                    WITH RECURSIVE category_tree AS (
                        -- Базовый случай: все категории, в которых есть товары
                        SELECT DISTINCT c.category_id, c.name, c.parent_id, c.extension
                        FROM category c
                        INNER JOIN product p ON p.category = c.category_id
                        WHERE c.parent_id = ?

                        UNION

                        -- Рекурсивный случай: дочерние категории с товарами
                        SELECT c.category_id, c.name, c.parent_id, c.extension
                        FROM category c
                        INNER JOIN category_tree ct ON c.parent_id = ct.category_id
                        INNER JOIN product p ON p.category = c.category_id
                    )
                    SELECT DISTINCT category_id, name, parent_id, extension
                    FROM category_tree 
                    ORDER BY name
                """, (parent_guid,))

            categories = []
            for row in self.cursor.fetchall():
                category_id, name, parent_id, extension = row
                image_filename = f"{category_id}.{extension}" if extension else None
                categories.append({
                    "guid": category_id,
                    "name": name,
                    "image": image_filename
                })
            return {'items': categories}

        except sqlite3.Error as e:
            print(f"Error getting categories with products hierarchy: {e}")
            return []

    def get_items_by_category(self, category_id):
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''SELECT 
                 p.guid||'.'||p.extension AS image, p.name AS text, p.guid, p.price, 0 as discount_price
             FROM product p 
             WHERE p.category = ? 
             ORDER BY p.name
         ''', (category_id,))
        return cursor.fetchall()

    def get_parent_category(self, category_id):
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''select parent_id from category where category_id = ?''', (category_id,))
        return(cursor.fetchone()[0])

    def get_product_by_id(self, product_guid):
        if not self.conn:
            self.connect()
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                p.guid, p.category, p.name, p.package, p.description, p.ingredients,
                p.weight, p.calorie, p.shelf_life, p.warm_time, p.price, p.extension,
                pk.name as package_name, 100 as discount_price, "Описание скидки" as discount_description
            FROM product p 
            LEFT JOIN package pk ON p.package = pk.guid 
            WHERE p.guid = ?
        ''', (product_guid,))
        row = cursor.fetchone()

        if row:
            db_dict = dict(row)
            return db_dict
        else:
            return {}
