import datetime
import logging
import io
import re
from ldif import LDIFParser
from collections import defaultdict
from ..db.exec_ql import MysqlPool
from ..data_format import res_format
from ..user.check import rule_displayname
from ..db.ldap_general import ldap_getobjectclass, ldap_format_tree, error_format
from ldap3 import Server, Connection, ALL, SUBTREE, SAFE_SYNC, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, BASE, LEVEL



def get_all(data_req):
    """
    获取指定ldap服务器的所有条目的信息和所有模板的信息
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

    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    sql_select_tem = "select * from sw_ldap_servers where server_name = %(server_name)s;"
    sql_select_data = {"server_name": server_name}
    res_db = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db:
        raise ZeroDivisionError(f"没有'{server_name}'这个LDAP服务器")

    cf = {
        "addr": res_db["server_addr"],
        "admin_dn": res_db["server_auth_dn"],
        "admin_password": res_db["server_auth_passwd"],
    }
    dn_base = res_db["server_base"]

    # 搜索并获取所有用户的children信息
    list_obj, res_dn_info = ldap_format_tree(dn_base, cf=cf)
    # 获取所有模板的信息
    list_class, list_attr = ldap_getobjectclass(cf=cf)

    list_obj_base = [

    ]

    data_res = {
        "obj_tree": list_obj,
        "obj_info": res_dn_info,
        "class": list_class,
        "attrs": list_attr,
        "dn_base": dn_base
    }

    return data_res


def add(data_req):
    """
    新建多个ldap条目(但是objectClass相同)
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        objectClass = data_req["objectClass"]
        # 条目列表, 每个元素都是字典, 含有attrs和dn
        list_dirs = data_req["dirs"]
        for d in list_dirs:
            attrs = d["attrs"]
            dn = d["dn"]

        # attrs = data_req["attrs"]
        # attrs["objectClass"] = objectClass
        # dn = data_req["dn"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
        select * from sw_ldap_servers where server_name = %(server_name)s;
    """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd, auto_bind=True)
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")
    else:
        try:
            # 组合数据
            data_ldap = defaultdict(dict)

            for d in list_dirs:

                dn = d["dn"]
                attrs = d["attrs"]
                data_ldap[dn] = {}

                # 查询这条dn
                status, result, response, _ = conn.search(dn, '(objectclass=*)', attributes=['*'], search_scope='BASE',)
                if status or response:
                    raise ZeroDivisionError(f"dn '{dn}' 已存在, 请检查: {status}, {result}")

                for k, v in attrs.items():
                    # 删除列表中的空值
                    # if isinstance(v, list):
                    #     v = [i for i in v if i]
                    data_ldap[dn][k] = v

            # print(data_ldap)
            # 发起修改
            for dn, dn_attrs in data_ldap.items():
                # dn_attrs["objectClass"] = objectClass
                logging.info(f"{server_name}准备新增{dn}; 属性: {dn_attrs}")
                status, result, response, _= conn.add(dn, object_class=objectClass, attributes=dn_attrs)
                if status:
                    # print(result)
                    logging.info(f"成功新增dn: {dn};objectClass: {objectClass}; 数据: {dn_attrs}")
                    pass
                else:
                    logging.error(f"{dn}新增失败: {result}")
                    fel = error_format(result['message'])
                    raise ZeroDivisionError(f"{dn}新增失败: {result['description']}, 详细原因: {fel}")

        except Exception as el:
            logging.exception(el)
            raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 新增数据失败: {el}")

    return {"ok": "ok"}

def update(data_req):
    """
    更新一个现有的ldap条目
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        objectClass = data_req["objectClass"]
        attrs = data_req["attrs"]
        attrs["objectClass"] = objectClass
        dn = data_req["dn"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
        select * from sw_ldap_servers where server_name = %(server_name)s;
    """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd, auto_bind=True)
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")
    else:
        try:
            # 查询这条dn
            status, result, response, _ = conn.search(dn, '(objectclass=*)', attributes=['*'], search_scope='BASE',)
            if not status or not response:
                raise ZeroDivisionError(f"dn '{dn}' 查询失败, 请检查")
            server_attrs = response[0]["attributes"]

            # 组合数据
            data_ldap = {}
            # 找出需要新增的字段
            list_add = list(set(attrs) - set(server_attrs))
            for i in list_add:
                data_ldap[i] = [(MODIFY_REPLACE, attrs[i])]
            # 找出需要删除的字段
            list_del = list(set(server_attrs) - set(attrs))
            for i in list_del:
                data_ldap[i] = [(MODIFY_DELETE, [])]
            # 找出需要覆盖式修改的字段
            list_re = list(set(server_attrs) & set(attrs))
            for i in list_re:
                data_ldap[i] = [(MODIFY_REPLACE, attrs[i])]

            print(data_ldap)
            # 发起修改
            status, result, response, _ = conn.modify(dn, data_ldap)
            if status:
                return {"ok": "ok"}
            else:
                logging.error(f"{dn}更新失败: {result}")
                fel = error_format(result['message'])
                raise ZeroDivisionError(f"{dn}更新失败: {result['description']}, 详细原因: {fel}")

        except Exception as el:
            logging.exception(el)
            raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 更新数据失败: {el}")


def delete(data_req):
    """
    批量删除指定服务器的dn
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        list_dn = data_req["list_dn"]
        if not isinstance(list_dn, list):
            res_format(err="传入的json数据格式错误: list_dn应为列表", code=10002)
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    rule_displayname(server_name)

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
            select * from sw_ldap_servers where server_name = %(server_name)s;
        """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd,
                          auto_bind=True)
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")

    else:
        list_dn_delete_tmp = []
        for dn in list_dn:
            status, result, response, _ = conn.search(dn, '(objectClass=*)', attributes=['*'])
            # 如果成功查询到了数据则开始操作
            if status:
                # 提取dn, 并按照len()的长度来降序排列, 确保长度最长的在前, 这样能从最底层开始删
                list_dn_children = [i["dn"] for i in response]
                # 追加入总列表
                list_dn_delete_tmp.extend(list_dn_children)
            # 没查到数据就直接返回删除成功
            else:
                logging.error(f"在{server_name}删除{dn}时没有查询到有效条目: {result}")

        # 去重并排序
        list_dn_delete = sorted(list(set(list_dn_delete_tmp)), key=len, reverse=True)
        # 开始删除
        for dn in list_dn_delete:
            try:
                status, result, response, _ = conn.delete(dn)
                if not status:
                    logging.error(f"在{server_name}删除{dn}时出错: {result}")
            except Exception as el:
                logging.error(f"在{server_name}删除{dn}时遇到了意外的错误: {el}")

    return {"ok": "ok"}


def move(data_req):
    """
    移动指定服务器的dn
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        dn = data_req["dn"]
        relative_dn = data_req["relative_dn"]
        superior = data_req["superior"]
        delete_old_dn = data_req["delete_old_dn"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)
    # relative_dn和superior应该至少有一个不为空
    if not relative_dn and not superior:
        return res_format(err="relative_dn和superior不能同时为空", code=10002)

    # relative_dn为空则自动赋予其值
    # if not relative_dn:
    #     relative_dn =

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
        select * from sw_ldap_servers where server_name = %(server_name)s;
    """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd,
                          auto_bind=True)
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")

    else:
        try:
            dn_old = ""
            dn_attrs_old = ""
            # 如果不删除原条目, 那么就先查出来一份, 因为delete_old_dn=False似乎不起作用
            status_s, result_s, response_s, __s = conn.search(dn, '(objectClass=*)',attributes=['*'],search_scope="BASE")
            if not status_s or not response_s:
                logging.error(f"{dn}变更时没找到指定条目: {result_s}")
                fel = error_format(result_s['message'])
                raise ZeroDivisionError(f"{dn}变更失败: {result_s['description']}, 详细原因: {fel}")
            else:
                dn_old = response_s[0]["dn"]
                dn_attrs_old = response_s[0]["attributes"]

            status, result, response, _ = conn.modify_dn(
                # 要操作的现dn
                dn=dn,
                # 要修改的rdn (dn的首段), 如果仅修改ou目录, 那么这个可以与dn值一致, 但不能为空
                relative_dn=relative_dn,
                # 是否删除旧条目, 默认True, 这里指为False反而会导致删不掉同值的命名属性值
                delete_old_dn=True,
                # 要修改ou的路径, 不修改就不需要定义
                new_superior=superior
            )

            if status:
                # 如果不删除原条目, 这里尝试手动新建一个
                if not delete_old_dn:
                    status, result, response, _ = conn.add(dn_old, attributes=dn_attrs_old)
                    print(result)

                return {"ok": "ok"}
            else:
                logging.error(f"{dn}变更失败: {result}")
                fel = error_format(result['message'])
                raise ZeroDivisionError(f"{dn}变更失败: {result['description']}, 详细原因: {fel}")

        except Exception as el:
            logging.exception(el)
            raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 变更数据失败: {el}")


def export(data_req):
    """
    导出指定dn的ldif格式文本
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        dn = data_req["dn"]
        export_tree = data_req["export_tree"]

    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)
    # relative_dn和superior应该至少有一个不为空
    # search_scope:["BASE", "LEVEL", "SUBTREE"] = "SUBTREE"
    if export_tree:
        search_scope = "SUBTREE"
    else:
        search_scope = "BASE"

    # relative_dn为空则自动赋予其值
    # if not relative_dn:
    #     relative_dn =

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
            select * from sw_ldap_servers where server_name = %(server_name)s;
        """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd,
                          auto_bind=True)
        # conn.response_to_ldif()
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")

    else:
        try:

            # 根据用户是否选择导出子条目而使用不同模式
            if export_tree:
                status, result, response, _ = conn.search(dn, '(objectClass=*)', attributes=['*'], search_scope="SUBTREE")
            else:
                status, result, response, _ = conn.search(dn, '(objectClass=*)', attributes=['*'],search_scope="BASE")
            if not status or not response:
                logging.error(f"找到指定条目{dn}: {result}")
                fel = error_format(result['message'])
                raise ZeroDivisionError(f"{dn}导出失败: {result['description']}, 详细原因: {fel}")
            else:

                def sort_dn(info_tmp):
                    return len(info_tmp['dn'])

                ldif_list = sorted(response, key=sort_dn)
                ldif_str_all = f"# 导出的顶层dn: {dn}\n" \
                    f"# 服务器: {server_name} ({server_addr})\n" \
                    f"# 导出范围: {'仅dn自身 (BASE)' if export_tree else 'dn自身及其所有子条目 (SUBTREE)'}\n" \
                    f'# 搜索过滤器: (objectClass=*)\n' \
                    f"# 总条数: {len(ldif_list)}\n" \
                    f"# 导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n\n"

                n = 1
                for r in ldif_list:
                    ldif_str_one = f"# 条目 {n}: {r['dn']}\ndn: {r['dn']}\n"
                    attrs = r["attributes"]
                    # 单独拿出来objectClass
                    for o in attrs["objectClass"]:
                        ldif_str_one += f"objectClass: {o}\n"
                    del attrs["objectClass"]
                    # 循环其他
                    for k, v in attrs.items():
                        if isinstance(v, list):
                            for vv in v:
                                if isinstance(vv, bytes):
                                    vv = vv.decode()
                                ldif_str_one += f"{k}: {vv}\n"
                        else:
                            if isinstance(v, bytes):
                                v = v.decode()
                            ldif_str_one += f"{k}: {v}\n"
                    ldif_str_one += "\n"
                    ldif_str_all += ldif_str_one
                    n += 1

                return ldif_str_all

        except Exception as el:
            logging.exception(el)
            raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 导出数据失败: {el}")


def upload(data_req):
    """
    导入ldif格式文本
    :param data_req:
    :return:
    """

    # 解析传入的信息
    try:
        server_name = data_req["server_name"]
        ldif_input = data_req["ldif"]
        force = data_req["force"]
    except Exception as el:
        logging.error("传入的json数据格式错误")
        logging.exception(el)
        return res_format(err="传入的json数据格式错误", code=10002)

    # 简单校验
    rule_displayname(server_name)

    data_add_tmp = {}

    # 解析ldif格式数据
    try:
        input_ldif_io = io.BytesIO(ldif_input.encode('utf-8'))
        parser = LDIFParser(input_ldif_io)
        # print(vars(parser))
        for dn, entry in parser.parse():
            # 可能有空数据, 疑似是 version 1 这种数据造成的
            if not dn:
                # print(entry)
                continue
            data_add_tmp[dn] = entry
        # print(data_add_tmp)
        # 按键的长度来排序, 使短的排前面
        data_add = dict(sorted(data_add_tmp.items(), key=lambda item: len(item[0])))
    except Exception as el:
        logging.error(f"解析ldif文本内容失败: {el}")
        return res_format(err=f"解析ldif文本内容失败: {el}")

    # 初始化数据库
    mp = MysqlPool()

    # 查询数据库中server_name的相关信息
    sql_select_tem = """
        select * from sw_ldap_servers where server_name = %(server_name)s;
    """
    sql_select_data = {"server_name": server_name}
    res_db_select = mp.fetch_one(sql_select_tem, sql_select_data)
    if not res_db_select:
        return res_format(err=f"{server_name}不存在")

    server_addr = res_db_select["server_addr"]
    server_base = res_db_select["server_base"]
    server_auth_dn = res_db_select["server_auth_dn"]
    server_auth_passwd = res_db_select["server_auth_passwd"]

    # 创建服务器对象
    server = Server(server_addr, get_info=ALL)
    try:
        conn = Connection(server, user=server_auth_dn, client_strategy=SAFE_SYNC, password=server_auth_passwd, auto_bind=True)
        # conn.response_to_ldif()
    except Exception as el:
        logging.exception(el)
        raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 验证失败, 请检查")

    else:
        try:

            # 先查, 看看有没有已存在的
            cf = {
                "addr": server_addr,
                "admin_dn": server_auth_dn,
                "admin_password": server_auth_passwd,
            }

            # 搜索并获取所有用户的children信息
            list_obj, res_dn_info = ldap_format_tree(server_base, cf=cf)
            # 创建前的校验
            list_k_exists = []
            list_k_nofather = []
            for k in data_add.keys():
                # 查看是不是已存在且未开启强制覆盖
                if k in res_dn_info.keys() and not force:
                    list_k_exists.append(k)
                # 查看k的父目录是否已存在或在列表中
                kf = ','.join(re.split(',', k)[1:])
                if kf not in res_dn_info.keys() and kf not in data_add.keys():
                    list_k_nofather.append(k)

            if list_k_exists:
                return res_format(err=f"拒绝导入: 已存在 {list_k_exists}")
            if list_k_nofather:
                return res_format(err=f"拒绝导入: {list_k_nofather} 的父条目不存在于服务器和待创建列表中")

            # 开始创建
            ns = 0
            ne = 0
            list_dn_err = []
            for k, v in data_add.items():
                # 看一下是否是强制创建, 是则先尝试删除
                if force:
                    conn.delete(k)
                # 创建并计数
                status, result, response, _ = conn.add(k, attributes=v)
                if status:
                    ns += 1
                else:
                    ne += 1
                    list_dn_err.append(k)

            data_res = {
                "num_success": ns,
                "num_error": ne,
                "list_dn_err": list_dn_err,
            }

            return data_res

            # status, result, response, _ = conn
            pass
        except Exception as el:
            logging.exception(el)
            raise ZeroDivisionError(f"LDAP服务器 '{server_name}' 导入数据失败: {el}")