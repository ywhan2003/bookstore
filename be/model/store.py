import logging
import os
import sqlite3 as sqlite
import pymysql


class Store:
    # database: str

    def __init__(self, host, user, password, database):
        # self.database = os.path.join(db_path, "be.db")
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cursor = conn.cursor()
            # cursor.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )

            sql = ('CREATE TABLE user ('
                   'user_id VARCHAR(50), password VARCHAR(50), balance INTEGER, token VARCHAR(50), terminal VARCHAR(50))'
                   )
            cursor.execute(sql)
            # cursor.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )
            #
            # cursor.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            #
            # cursor.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            # )
            #
            # cursor.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )
            #
            # conn.commit()
        except sqlite.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self) -> sqlite.Connection:
        return pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)


database_instance: Store = None


def init_database(host, user, password, database):
    global database_instance
    database_instance = Store(host, user, password, database)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
