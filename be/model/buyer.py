import sqlite3 as sqlite
from datetime import datetime
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""

        cursor = self.conn.cursor()

        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id) + (order_id,)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id) + (order_id,)
        uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

        sql_get_book = ('SELECT book_id, stock_level, price FROM store '
                         'WHERE store_id = %s AND book_id = %s')

        sql_update_stock = ('UPDATE store SET stock_level = stock_level - %s '
                            'WHERE store_id = %s and book_id = %s and stock_level >= %s')

        sql_insert_order = ('INSERT INTO new_order(order_id, user_id, store_id, time, status) '
                            'VALUES (%s, %s, %s, %s, %s)')

        sql_insert_detail = ('INSERT INTO orders(order_id, book_id, count, price) '
                             'VALUES (%s, %s, %s, %s)')
        try:

            cursor.execute(sql_insert_order, (uid, user_id, store_id, datetime.now(), 0))
            for book_id, count in id_and_count:
                cursor.execute(sql_get_book, (store_id, book_id))

                row = cursor.fetchone()
                if row is None:
                    self.conn.rollback()
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                price = row[2]

                if stock_level < count:
                    self.conn.rollback()
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor.execute(sql_update_stock, (count, store_id, book_id, count))

                cursor.execute(sql_insert_detail, (uid, book_id, count, price))



            self.conn.commit()
            order_id = uid
        except Exception as e:
            self.conn.rollback()
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            self.conn.rollback()
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        finally:
            cursor.close()
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.execute(
                "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor = conn.execute(
                "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
                (store_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = conn.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
                (order_id,),
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute(
                "UPDATE user set balance = balance - ?"
                "WHERE user_id = ? AND balance >= ?",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor = conn.execute(
                "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
                (total_price, buyer_id),
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            cursor = conn.execute(
                "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor = conn.execute(
                "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.execute(
                "SELECT password  from user where user_id=?", (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE user SET balance = balance + ? WHERE user_id = ?",
                (add_value, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
