"""数据库连接配置"""
import pymysql

DB = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'db_sms',
    'charset': 'utf8mb4',
}


def connect():
    return pymysql.connect(**DB)
