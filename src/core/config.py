"""数据库连接配置"""
import os
import pymysql
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

load_dotenv()

DB = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "db_sms"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

# 给命令行脚本（main.py / import_data.py / reset_data.py）用，直连，不需要池


def connect():
    """创建并返回原生 pymysql 连接"""
    return pymysql.connect(**DB)


# ===================== Streamlit 连接池方案 =====================
_DB_URL = (
    f"mysql+pymysql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}"
    f"/{DB['database']}?charset={DB['charset']}"
)


@st.cache_resource
def get_engine():
    """全局唯一连接池引擎，Streamlit 自动缓存生命周期"""
    return create_engine(
        _DB_URL,
        poolclass=QueuePool,
        pool_size=5,           # 常驻空闲连接数
        max_overflow=10,       # 峰值额外临时连接数
        pool_pre_ping=True,    # 核心：取连接前自动检测，失效自动重连
        pool_recycle=3600,     # 1小时强制回收连接，规避MySQL 8小时超时
        pool_use_lifo=True,    # 后进先出，尽量复用热连接，稳定性更好
    )


def get_connection():
    """
    从连接池获取一个**原生 pymysql 连接**
    上层业务代码无需任何修改，兼容所有 cursor / callproc / fetchall 写法
    页面渲染完成后连接自动关闭并放回连接池
    """
    # raw_connection() 返回底层原生 pymysql 连接对象，100% 兼容原有写法
    return get_engine().raw_connection()
