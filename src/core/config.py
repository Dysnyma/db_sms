"""数据库连接配置"""

import pymysql
import streamlit as st

DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "db_sms",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}


def connect():
    """创建并返回数据库连接"""
    return pymysql.connect(**DB)


@st.cache_resource
def get_connection():
    """应用级共享数据库连接（Streamlit 自动管理生命周期）"""
    return pymysql.connect(**DB)
