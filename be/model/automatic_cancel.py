# import sqlite3 as sqlite
# from datetime import datetime
# import uuid
# import json
# import logging
#
# import pymysql
#
# from be.model import db_conn
# from be.model import error
#
#
# class Cancel(db_conn.DBConn):
#     def __init__(self):
#         db_conn.DBConn.__init__(self)
#
#     def cancel_order(self):
#         cursor = self.conn.cursor()
#
#         sql = 'UPDATE new_order SET status = -1 WHERE TIMESTAMPDIFF(HOUR, time, NOW()) >24 AND status = 0'
#
#         cursor.execute(sql)
#
#
# if __name__ == '__main__':
#     cancel = Cancel()
#     while True:
#         cancel.cancel_order()
