import logging
from ..db.exec_ql import MysqlPool
from ..data_format import res_format
from ..user.check import rule_displayname


def get_all(data_req):
    # 初始化数据库
    mp = MysqlPool()

    # 查看是不是已有这个名字
    sql_select_tem = """
        select * from sw_ldap_servers;
    """
    res_db_select = mp.fetch_all(sql_select_tem)

    # 返回字典, 而不是列表
    data_res = {}
    for i in res_db_select:
        server_name = i["server_name"]
        data_res[server_name] = i

    return data_res


def add(data_req):
    """
    新增一个ldap服务器连接
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        server_addr = data_req["server_addr"]
        server_base = data_req["server_base"]
        server_auth_dn = data_req["server_auth_dn"]
        server_auth_passwd = data_req["server_auth_passwd"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 查看是不是已有这个名字
    sql_select_tem = f"""
        select server_name from sw_ldap_servers where server_name = :server_name;
    """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if res_db_select:
        return res_format(err=f"{server_name}已存在")

    # 创建
    sql_create_tem = """
        insert into sw_ldap_servers (server_name,server_addr,server_base,server_auth_dn,server_auth_passwd,date_create,date_update)
        values (:server_name,:server_addr,:server_base,:server_auth_dn,:server_auth_passwd,DATETIME('now'),DATETIME('now'))
    """
    sql_create_data = {
        "server_name": server_name,
        "server_addr": server_addr,
        "server_base": server_base,
        "server_auth_dn": server_auth_dn,
        "server_auth_passwd": server_auth_passwd,
    }
    mp.transaction(sql_create_tem, sql_create_data)

    return {"ok": "ok"}


def update(data_req):
    """
    新增一个ldap服务器连接
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        server_addr = data_req["server_addr"]
        server_base = data_req["server_base"]
        server_auth_dn = data_req["server_auth_dn"]
        server_auth_passwd = data_req["server_auth_passwd"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 更新
    sql_create_tem = """
        update sw_ldap_servers set
            server_addr = :server_addr,
            server_base = :server_base,
            server_auth_dn = :server_auth_dn,
            server_auth_passwd = :server_auth_passwd,
            date_update = DATETIME('now')
        where server_name = :server_name;
    """
    sql_create_data = {
        "server_name": server_name,
        "server_addr": server_addr,
        "server_base": server_base,
        "server_auth_dn": server_auth_dn,
        "server_auth_passwd": server_auth_passwd,
    }
    mp.transaction(sql_create_tem, sql_create_data)

    return {"ok": "ok"}



def delete(data_req):
    """
    删除一个ldap服务器连接
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 更新
    sql_create_tem = """
        delete from sw_ldap_servers
        where server_name = :server_name;
    """
    sql_create_data = {
        "server_name": server_name,
    }
    mp.transaction(sql_create_tem, sql_create_data)

    return {"ok": "ok"}

