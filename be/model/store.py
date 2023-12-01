import logging
import os
import sqlite3 as sqlite
import pymysql


class Store:
    # database: str
    conn: pymysql.Connection
    def __init__(self, host, user, password, database):
        # self.database = os.path.join(db_path, "be.db")
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.init_tables()

    def init_tables(self):
        self.conn = self.get_db_conn()
        cursor = self.conn.cursor()
        sql1 = (
            'CREATE TABLE user ('
            'user_id VARCHAR(300) PRIMARY KEY , password VARCHAR(300), '
            'balance INTEGER, token VARCHAR(300), terminal VARCHAR(300),'
            'INDEX index_user (user_id))'
        )

        sql2 = (
            'CREATE TABLE user_store ('
            'user_id VARCHAR(300), store_id VARCHAR(300) PRIMARY KEY,'
            'FOREIGN KEY (user_id) REFERENCES user(user_id),'
            'INDEX index_store (store_id))'
        )

        sql3 = (
            'CREATE TABLE store ('
            'store_id VARCHAR(300), book_id VARCHAR(300), title VARCHAR(30), price SMALLINT, '
            'tags VARCHAR(30), author VARCHAR(30),'
            'content VARCHAR(1000), book_intro VARCHAR(1000),stock_level SMALLINT,'
            'PRIMARY KEY (store_id, book_id),'
            'FOREIGN KEY (store_id) REFERENCES user_store(store_id),'
            'INDEX index_store_book (store_id, book_id),' # 加一个复合索引
            'FULLTEXT INDEX index_title(title),'
            'FULLTEXT INDEX index_tags(tags),'
            'FULLTEXT INDEX index_author(author),'
            'FULLTEXT INDEX index_content(content),'
            'FULLTEXT INDEX index_book_intro(book_intro))'
        )

        sql4 = (
            'CREATE TABLE new_order ('
            'order_id VARCHAR(300) PRIMARY KEY , user_id VARCHAR(300), store_id VARCHAR(300), time TIMESTAMP,'
            'FOREIGN KEY (user_id) REFERENCES user(user_id), '
            'FOREIGN KEY (store_id) REFERENCES user_store(store_id),'
            'INDEX index_order (order_id))'
        )

        sql5 = (
            'CREATE TABLE orders ('
            'order_id VARCHAR(300), book_id VARCHAR(300), count SMALLINT, price SMALLINT,'
            'FOREIGN KEY (order_id) REFERENCES new_order(order_id),'
            'PRIMARY KEY (order_id, book_id), '
            'INDEX index_order_book (order_id, book_id))'
        )
        try:
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            cursor.execute(sql4)
            cursor.execute(sql5)
        except Exception as e:
            logging.error(e)
            self.conn.rollback()
        finally:
            cursor.close()
            self.conn.close()


    def get_db_conn(self) -> pymysql.Connection:
        return pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)


database_instance: Store = None


def init_database(host, user, password, database):
    global database_instance
    database_instance = Store(host, user, password, database)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()