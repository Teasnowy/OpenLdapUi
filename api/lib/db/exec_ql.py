import functools
import logging
import os
import threading
import time
import sqlite3

import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB

# 全局锁
# singleton_lock = threading.RLock()


def singleton(cls_tmp):
    """
    同步锁, 接受一个类作为参数, 确保多线程环境下的类的单实例模式
    """
    # 保存原始 __new__ 和 __init__
    cls_tmp.__new_original__ = cls_tmp.__new__

    # 这里定义的singleton_new稍后会取代原__new__
    # 这里使用了 functools.wraps，使得装饰后的函数保留原始函数的签名和元数据
    @functools.wraps(cls_tmp.__new__)
    def singleton_new(cls, *args, **kwargs):
        # RLock() 是一种递归锁，与普通锁不同，递归锁允许同一个线程多次获得锁而不会导致死锁。这一步的目的是防止多个线程同时创建类实例, 防止小概率事件
        # 当一个线程获取锁时，其他线程会被阻塞，直到该线程释放锁，从而确保线程安全, 这里仅仅是定义锁, 并没有触发
        with threading.RLock():
            # 检查是否已有实例
            # 从类的 __dict__ 中检查是否已经存在实例 __it__。如果已经存在一个实例，直接返回该实例，避免再次创建，从而确保单例模式的效果
            it = cls.__dict__.get('__it__')
            if it is not None:
                return it

            # 如果类实例尚不存在，则调用原始的 __new__ 方法创建新实例，并将其存储在类属性 __it__ 中
            # 这样一来，后续的线程如果尝试创建该类的实例，会直接返回这个已经创建好的实例。
            cls.__it__ = it = cls.__new_original__(cls, *args, **kwargs)
            # 调用保存的原始 __init__ 方法 it.__init_original__(*args, **kwargs)，初始化实例
            it.__init_original__(*args, **kwargs)
            return it

    # 将类的 __new__ 方法替换为自定义的 singleton_new 方法，这样每次创建新实例时都会经过同步锁的检查，确保单例
    cls_tmp.__new__ = singleton_new
    # 将类的原始 __init__ 保存为 __init_original__，供新创建实例时使用
    cls_tmp.__init_original__ = cls_tmp.__init__
    # 将类的 __init__ 方法替换为 object.__init__。
    # 之所以这样做，是为了防止多次调用 __init__。在 Python 中，每次调用 __new__ 后，__init__ 都会执行。
    # 而在单例模式下，实例只需要初始化一次，所以替换为 object.__init__，使得后续的 __init__ 调用变成空操作
    cls_tmp.__init__ = object.__init__

    # 返回修改后的类
    return cls_tmp


@singleton
class MysqlPool(object):
    """
    全局共享的数据库连接池, 在启动时就已经初始化了
    """
    def __init__(self):
        # self.conn = sqlite3.connect("server.db")
        logging.info('准备数据库链接')

    def connect(self):
        try:
            dir_app = os.path.dirname(os.path.abspath(__file__))
            # print(f"{dir_app}/server.db")
            conn = sqlite3.connect(f"{dir_app}/server.db")
            conn.row_factory = self.dict_factory
            cursor = conn.cursor()
        except Exception as el:
            logging.error("数据库连接失败")
            logging.exception(el)
            raise ZeroDivisionError("后端数据库好像出了问题")
        return conn, cursor

    def connect_close(self, conn, cursor):
        cursor.close()
        conn.close()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def fetch_all(self, sql, args=None) -> list[dict]:
        """
        查询数据, 返回所有结果, 返回的是个列表
        :param sql: sql模板或者完整sql
        :param args: 要填入模板中的数据
        :return:
        """
        conn, cursor = self.connect()
        try:
            if args is None:
                # s = sql % args
                cursor.execute(sql)
            else:
                cursor.execute(sql, args)
            record_list = cursor.fetchall()
        finally:
            self.connect_close(conn, cursor)
        return record_list

    def fetch_one(self, sql, args=None) -> dict:
        """
        查询, 但只返回一条数据, 返回的是字典
        :param sql: sql模板或者完整sql
        :param args: 要填入模板中的数据
        :return:
        """
        conn, cursor = self.connect()
        if args:
            # s = sql % args
            # print(s)
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        result = cursor.fetchone()
        return result

    def transaction(self, sql, args=None, is_list=False):
        """
        执行事务的函数
        :param sql: sql模板或完整sql, 如果is_list为True, 那么应为列表
        :param args: 要填写的值, 字典或元组
        :param is_list: 是否是列表 (sql语句中不支持带;号, 此时args里应包含所有sql模板内的值)
        :return:
        """
        row = None
        conn, cursor = self.connect()
        try:
            if is_list:
                row = []
                for s in sql:
                    if args:
                        # l = s % args
                        r = cursor.execute(s, args)
                    else:
                        r = cursor.execute(s)
                    row.append(r)
            else:
                if args:
                    # s = sql % args
                    row = cursor.execute(sql, args)
                else:
                    row = cursor.execute(sql)
        except Exception as el:
            conn.rollback()
            logging.error(f"执行sql时遇到错误, 触发事务回滚: {el}")
            logging.exception(el)
            raise ZeroDivisionError("数据库或语句异常")
        else:
            conn.commit()
        self.connect_close(conn, cursor)
        return row



@singleton
class MysqlOnce:
    """
    只提供单次使用的数据库连接
    """
    def __init__(self, host, port, user, password, database, charset='utf8', remarks=""):
        # 初始化数据库连接
        self.conn = pymysql.connect(user=user, password=password, host=host, port=port, charset=charset, database=database)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        self.test_str = 123456
        logging.info('初始化数据库连接')

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def select_all(self, sql_select, res="fetchall" ):
        """
        执行查询语句, 返回所有结果
        :param sql_select: 执行的select语句
        :param res: 返回多少条数据, fetchall(默认): 全部, int数字: 获取指定条数
        """
        self.cursor.execute(sql_select)
        if isinstance(res, int):
            result = self.cursor.fetchmany(res)
        else:
            result = self.cursor.fetchall()
        return result

    def commit(self, sql, args=None):
        # 开启事务
        self.conn.begin()
        try:
            # 推荐使用占位符和参数的方式, 这样不用自己组合引号了, 也防止sql注入
            self.cursor.execute(sql, args)
        except Exception as e:
            logging.error(f'触发事务回滚: {sql} 值: {args}')
            logging.exception(e)
            self.conn.rollback()
            raise ZeroDivisionError("SQL执行失败, 触发事务回滚")
        else:
            logging.info(f"sql执行成功: {sql} 值: {args}")
            self.conn.commit()

    def close(self):
        """
        关闭数据库连接
        """
        self.cursor.close()
        self.conn.close()



def manual_substitute(list_sql, data):
    """
    手动替换 SQL 语句中的占位符为实际的参数值, 用于前端展示

    参数:
    list_sql: 列表中元素应为元组, 元组第一位是带占位符的sql, 第二位是值

    返回:
    列表: 替换占位符后的 SQL 语句。
    """
    list_sql_str = []
    # 检查参数类型是否是字符串，如果是字符串，则添加引号
    for sql in list_sql:
        # 使用参数替换占位符
        substituted_sql = sql % data
        # print(substituted_sql)
        list_sql_str.append(substituted_sql)
    return list_sql_str