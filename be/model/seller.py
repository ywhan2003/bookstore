import json
import sqlite3 as sqlite
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if self.book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)

        book_info_json = json.loads(book_json_str)

        title = book_info_json.get("title")
        tags = book_info_json.get("tags")
        tags = ",".join(tags)
        author = book_info_json.get("author")
        content = book_info_json.get("content")
        book_intro = book_info_json.get("book_intro")
        price = book_info_json.get("price")


        cursor = self.conn.cursor()

        sql = ('INSERT INTO store(store_id, book_id, title, price, tags, author, content, book_intro, stock_level) '
               'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)')
        try:
            cursor.execute(sql, (store_id, book_id, title, price, tags, author, content, book_intro, stock_level))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            cursor.close()
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not self.book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)

        cursor = self.conn.cursor()
        sql = 'UPDATE store SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s'

        try:
            cursor.execute(sql, (add_stock_level, store_id, book_id))
            self.conn.commit()
        except sqlite.Error as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            cursor.close()
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if self.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)

        cursor = self.conn.cursor()

        sql = 'INSERT INTO user_store(user_id, store_id) VALUES (%s, %s)'
        try:
            cursor.execute(sql, (user_id, store_id))
            self.conn.commit()
        except sqlite.Error as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            cursor.close()
        return 200, "ok"
