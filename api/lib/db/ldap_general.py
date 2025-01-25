from ldap3 import Server, Connection, ALL, SUBTREE, SAFE_SYNC, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from .exec_ql import MysqlPool
from collections import defaultdict
import logging
import re


def format_ou_users(dict_ldap_users, search_attrs):
    """
    将ldap中搜到的用户格式化, 包括:
        对比数据库中用户来标记是否已收录此用户;
        将ldap属性名转义为对应添加用户时的别名
    :param dict_ldap_users:
    :param search_attrs:
    :return:
    """
    # 初始化数据库连接池
    mp = MysqlPool()
    # 获取已有的用户的所有dn, 并去重, 用来甄别已有的ldap用户
    # sql_select_dn_tem = """
    #     select DISTINCT ldap_dn, account from sw_user where ldap_dn is not null;
    # """
    sql_select_dn_tem = """
        select 
            u.ldap_dn, u.account,
            GROUP_CONCAT(DISTINCT ug.group_id ORDER BY ug.group_id SEPARATOR ',') AS groups,
            GROUP_CONCAT(DISTINCT ru.role_id ORDER BY ru.role_id SEPARATOR ',') AS roles
        from 
            sw_user u
            left join sw_roleuser ru on u.account = ru.account
            left join sw_usergroup ug on u.account = ug.account
        where 
            ldap_dn is not null
        GROUP BY u.account;
    """
    list_res_db_dn = mp.fetch_all(sql_select_dn_tem)
    # 返回结果有可能是空的
    res_db_dn = {}
    if list_res_db_dn:
        # 取出数据库中的所有已存在dn
        # res_db_dn = [i["ldap_dn"] for i in list_res_db_dn]
        for i in list_res_db_dn:
            res_db_dn[i["ldap_dn"]] = i
    # 取出当前ldap所有用户的dn
    res_ldap_dn = list(dict_ldap_users.keys())

    # 定义要返回的数据
    data_res = defaultdict(dict)
    data_res = {}

    # 如果值是列表, 那么只取第一个值
    for k, v in dict_ldap_users.items():
        data_res[k] = {}
        # 将dn加入values
        data_res[k]["dn"] = k
        for kk, attr_name in search_attrs.items():
            attr_value = dict_ldap_users[k][attr_name]
            # logging.info(f"将{data_res[k]['dn']} 的 {kk} 赋值 {attr_value}")
            if isinstance(attr_value, list):
                if attr_value:
                    # 如果是列表且不为空, 则取第一个值
                    data_res[k][kk] = attr_value[0]
                else:
                    data_res[k][kk] = ""
            else:
                data_res[k][kk] = attr_value
            # logging.info(f"将{k} 的 {kk} 最终为 {data_res[k][kk]}")
    # logging.info(res_db_dn)
    # 将dict_ldap_users中的已存在于数据库中的dn单独标记, 而不是删除
    for dn in res_ldap_dn:
        if dn in res_db_dn.keys():
            # del dict_ldap_users[dn]
            data_res[dn]["is_exists"] = True
            # 这里就返回已经在库里的account账户
            data_res[dn]["account"] = res_db_dn[dn]["account"]
            # group_list = re.split(',', res_db_dn[dn]["groups"] or "") if res_db_dn[dn]["groups"] else []
            # logging.info(group_list)
            data_res[dn]["groups"] = re.split(',', res_db_dn[dn]["groups"] or "") if res_db_dn[dn]["groups"] else []
            data_res[dn]["roles"] = re.split(',', res_db_dn[dn]["roles"] or "") if res_db_dn[dn]["roles"] else []
        else:
            data_res[dn]["is_exists"] = False
    # logging.info(f"规整后的ldap用户列表: {data_res}")
    return data_res


def ldap_getobjectclass(cf:dict):
    """
    获取目标ldap服务器的模板信息, 包括其必填属性, 可选属性等等
    :param cf: ldap服务器配置, 不传则默认从配置文件里的ldap服务器取数据
    :return:
    """

    ldap_addr = cf["addr"]
    ldap_user = cf["admin_dn"]
    ldap_passwd = cf["admin_password"]

    # 存储模板类结果
    dict_schema_info = {}
    # 存储字段信息
    dict_attribute_info = {}

    dn_class = "cn=schema,cn=config"
    regexp_class = "(objectClass=olcSchemaConfig)"

    # 创建服务器对象
    server = Server(ldap_addr, get_info=ALL)

    # 创建连接对象
    try:
        conn = Connection(server, user=ldap_user, client_strategy=SAFE_SYNC, password=ldap_passwd, auto_bind=True)
        # print("LDAP 登录成功")
    except Exception as el:
        logging.error(el)
        raise ZeroDivisionError("登录失败, 检查用户名和密码")

    # 在这里可以进行其他 LDAP 操作，例如搜索
    # conn.search('ou=users,dc=example,dc=com', '(objectClass=*)', attributes=['cn', 'sn'])
    else:
        # 提前参考官方文档写好各字段类型
        dict_attr_types = {
            "1.3.6.1.4.1.1466.115.121.1.15": "Unicode 字符串",
            "1.3.6.1.4.1.1466.115.121.1.12": "ldap唯一索引",
            "1.3.6.1.4.1.1466.115.121.1.27": "整数值",
            "1.3.6.1.4.1.1466.115.121.1.36": "仅包含数字和空格",
            "1.3.6.1.4.1.1466.115.121.1.5": "二进制数据",
            "1.3.6.1.4.1.1466.115.121.1.7": "布尔值",
            "1.3.6.1.4.1.1466.115.121.1.24": "日期和时间",
            "1.3.6.1.4.1.1466.115.121.1.25": "日期和时间",
            "1.3.6.1.4.1.1466.115.121.1.26": "ASCII 字符",
            "1.3.6.1.4.1.1466.115.121.1.40": "二进制数据",
            "1.3.6.1.4.1.1466.115.121.1.4": "X.509 数字证书",
            "1.3.6.1.4.1.1466.115.121.1.8": "dn表达式",
            "1.3.6.1.4.1.1466.115.121.1.38": "OID",
            "1.3.6.1.4.1.1466.115.121.1.50": "电话号码",
        }

        # 获取所有模板信息
        server_schema_info = conn.server.schema.object_classes
        for k, v in server_schema_info._store.items():
            # 可以用vars(v)看看属性对应的字段名
            # print(vars(v))
            # if v.name[0] == 'top':
            #     print(vars(v))
            tmp_schema_info = {
                "tem_oid": v.oid,
                "tem_name_list": v.name,
                "tem_desc": v.description,
                "tem_must_list": v.must_contain,
                "tem_may_list": v.may_contain,
                "tem_sup_list": v.superior,
                # 记录第一名字, 因为openldap中就算定义了其他名字, 最终在dn上的还是第一个名字
                "tem_name_fri": v.name[0],
                # kind, 字符串, 表示这个对象类的类型:
                # ABSTRACT抽象对象类(不能定义在条目中, 只能被其他结构化或辅助对象类继承);
                # STRUCTURAL结构化对象类, 每个条目至少有一个结构化对象类;
                # AUXILIARY辅助对象类, 提供额外的属性(不能单独出现在条目中)
                "kind": v.kind
            }
            # 对名字列表进行循环, 防止多个名字的现象出现
            for n in v.name:
                dict_schema_info[n] = tmp_schema_info
                # print(f"{n}: {tmp_schema_info}")
        # print(dict_schema_info)

        # 获取所有字段信息
        # 记录有多个名字的属性的字典
        server_attribute_info = conn.server.schema.attribute_types
        # print(vars(server_attribute_info))
        for k, v in server_attribute_info.items():
            # print(vars(v))
            # break
            # if v.name[0] == 'javaObject' or v.name[0] == 'person':
            #     print(vars(v))
            # 这里是看一下有没有预先对属性的类型定义, 有的话就提取
            if v.syntax in dict_attr_types.keys():
                attr_type = dict_attr_types[v.syntax]
            else:
                attr_type = None

            tmp_attribute_info = {
                "attr_oid": v.oid,
                "attr_name_list": v.name,
                "attr_desc": v.description,
                # 布尔值, 表示是否是仅单值的属性, false则表示多值
                "attr_isSingle": v.single_value,
                # 在哪些objectClasses的可选列表中, 不全, sup的不会被记录
                # "attr_mandatory_list": v.mandatory_in,
                # 在哪些objectClasses的必选列表中, 不全, sup的不会被记录
                # "attr_optional_list": v.optional_in,
                # 值的类型, 是一串数字和小数点, 难以阅读
                "attr_syntax": v.syntax,
                # 值的类型, 被转义为可读的中文, 在dict_attr_types中预制的
                "attr_type": attr_type,
                # 记录第一名字, 因为openldap中就算定义了其他名字, 最终在dn上的还是第一个名字
                "attr_name_fri": v.name[0],
            }
            for n in v.name:
                dict_attribute_info[n] = tmp_attribute_info

        # 将模板类和各属性整理为一个字典
        for tem_name, tem_info in dict_schema_info.items():

            list_attr_may = tem_info["tem_may_list"]
            list_attr_must = tem_info["tem_must_list"]

            # 无限循环提取被SUP引用的模板的属性列表
            def analysis_object_attrs(sup_name_list):
                for sup_name in sup_name_list:
                    # 如果引用列表不为空
                    if sup_name in dict_schema_info:
                        sup_schema_info = dict_schema_info[sup_name]
                        # 与当前列表合并
                        list_attr_may.extend(sup_schema_info["tem_may_list"])
                        list_attr_must.extend(sup_schema_info["tem_must_list"])
                        sup_sup = sup_schema_info["tem_sup_list"]
                        # 如果被引用的列表仍然后引用列表, 那么就用本函数再次处理, 无限循环
                        if sup_sup:
                            analysis_object_attrs(sup_sup)
                return list_attr_may, list_attr_must

            # 获取可选属性列表
            tem_sup_list = tem_info["tem_sup_list"]
            if tem_sup_list:
                list_attr_may, list_attr_must = analysis_object_attrs(tem_sup_list)

            # 去重, 且将must中的字段也加入may
            if list_attr_must:
                list_attr_may.extend(list_attr_must)
                list_attr_must = list(set(list_attr_must))
            if list_attr_may:
                list_attr_may = list(set(list_attr_may))

            # 将拿到的信息汇入模板信息的字典中
            tem_info["tem_may_list"] = list_attr_may
            tem_info["tem_must_list"] = list_attr_must

        # 去掉不能实例化的抽象对象类, 减轻前端的判断逻辑
        list_abstract = []
        for tem_name, tem_info in dict_schema_info.items():
            if tem_info['kind'] == 'ABSTRACT' and 'top' not in tem_info['tem_name_list']:
                list_abstract.append(tem_name)
        for tem_name in list_abstract:
            del dict_schema_info[tem_name]

    return dict_schema_info, dict_attribute_info
    # return {}, {}


def ldap_format_tree(dn_base, cf:dict):
    """
    搜索所有条目并将search到的数据转化为前端tree组件能理解的children结构
    :param cf: ldap服务器配置, 不传则默认从配置文件里的ldap服务器取数据
    :param dn_base: 要搜索的域
    :return:
    """

    ldap_addr = cf["addr"]
    ldap_user = cf["admin_dn"]
    ldap_passwd = cf["admin_password"]

    res_tree = []
    res_dn_info = {}

    dn_class = "cn=schema,cn=config"
    regexp_class = "(objectClass=olcSchemaConfig)"

    # 创建服务器对象
    server = Server(ldap_addr, get_info=ALL)

    # 创建连接对象
    try:
        conn = Connection(server, user=ldap_user, client_strategy=SAFE_SYNC, password=ldap_passwd, auto_bind=True)
        # logging.info("LDAP 登录成功 ~~~~~")
    except Exception as el:
        logging.error(el)
        raise ZeroDivisionError("登录失败, 检查用户名和密码")
    # 在这里可以进行其他 LDAP 操作，例如搜索
    # conn.search('ou=users,dc=example,dc=com', '(objectClass=*)', attributes=['cn', 'sn'])

    else:
        base_info = {}
        # 查询base
        status_base, result_base, response_base, __base = conn.search(dn_base, '(objectclass=*)', attributes=['*'], search_scope="BASE")
        if status_base:
            pass
            # for r in response_base:
            #     if r["dn"] == dn_base:
            #         base_info["dn"] = dn_base
            #         base_info["entry"] = dn_base
            #
            #         attrs_tmp = r["attributes"]
            #         base_info["objectClass"] = attrs_tmp["objectClass"]
            #         del attrs_tmp["objectClass"]
            #         res_dn_info[dn_base] = attrs_tmp
            # if not base_info:
            #     raise ZeroDivisionError(f"查询base域为空")
            # print(base_info)
            # print(res_dn_info)

        else:
            raise ZeroDivisionError(f"查询base域{dn_base}失败, 请先创建后再查询")
        # 查询所有子条目
        # 返回结果是一个元组 (执行状态-布尔值, 执行的结果-字典, 响应的数据-字典或None, 被操作条目自身的信息-字典)
        status, result, response, _ = conn.search(
            # 要搜索的起点的dn
            dn_base,
            # 条件限制, 括号包裹, 必须包含objectClass这个条件, 哪怕值为*; 支持与或否*, 参考openldap的笔记
            '(objectclass=*)',
            # 返回搜索到的dn的哪些属性, 也可以使用['*']表示全部, 不需要区分大小写
            # 但是属性必须存在于这个ldap的配置中(所有模板范围内)
            attributes=['*']
        )

        for r in response:
            dn = r["dn"]

            # if dn == dn_base:
            #     continue

            # 这里要注意, attrs里的很多内容有可能是byte格式, 注意不要影响其他功能, 比如flask的jsonify
            attrs = r["attributes"]
            attrs_format = {}

            # 规整attrs内的数据, 去掉不能被flask的jsonify格式化的
            for k, v in attrs.items():
                if isinstance(v, list):
                    attr_data = []
                    for a in v:
                        # 如果是字节流, 则转为字符串
                        if isinstance(a, bytes):
                            a = a.decode()
                        attr_data.append(a)
                else:
                    # 如果是字节流, 则转为字符串
                    if isinstance(v, bytes):
                        v = v.decode()
                    attr_data = v
                attrs_format[k] = attr_data

            # 将objectClass单独拿出来
            object_class = attrs_format["objectClass"]
            del attrs_format["objectClass"]

            # 这里没有必要引用
            # list_tree = res_tree
            # logging.info(f"开始 {dn}")
            # 将dn_base, 以及它前面有可能的逗号去掉, 因为目录结构中的起点就是dn_base, 于是取相对路径
            k_str_del_base = re.sub(f',?{dn_base}$', '', dn)
            # 将这个相对路径转为列表, 方便区分当前处于哪一层
            list_dir = re.split(',', k_str_del_base)
            # 使列表倒序, 因为dn的路径是从右向左的
            list_dir.reverse()

            # 定义这个能嵌套处理的函数, 传入的参数是res_tree, res_tree在函数内会被自动引用子层的children, 但是不影响下一次大循环
            def add_tree(l):
                # for d in list_dir:
                # 这里抛弃循环, 直接用第一个值, 用来表示当前所在层
                d = list_dir[0]
                # 检查当前层的各个字典有没有本次的层的名字
                if d not in [i['entry'] for i in l]:
                    # 没有就给个默认值, base除外
                    if dn != dn_base:
                        l.append({
                            "entry": d,
                            "dn": dn,
                            "children": [],
                        })
                    else:
                        base_info["entry"] = dn
                        base_info["dn"] = dn

                    # 由于是追加, 那么这次新增的字典就是最后一个元素
                    index_new = len(l) - 1
                else:
                    # 如果有, 那么就仅记录这个已经存在的层的下标号码, 用于传递给下一次嵌套add_tree
                    index_new = [i for i in range(len(l)) if l[i]['entry'] == d][0]
                # 如果不是最后一层, 则替换引用本层的children
                if len(list_dir) > 1:
                    # 引用当前所在层
                    l = l[index_new]["children"]
                    # 删掉本层, 这是为了
                    del list_dir[0]
                    # 嵌套函数, 此时已经del了本层, 就达成了无限嵌套的效果, 直到最后一层
                    add_tree(l)
                # 如果是本层, 则直接将attrs信息添加
                else:
                    # l[index_new]["attrs"] = attrs_format
                    # 字段信息单独放一个字典里, 因为vue的tree v2有底层数据刷新不及时的问题
                    res_dn_info[dn] = {
                        "attrs": attrs_format,
                        "objectClass": object_class
                    }
                    # dn单独存储
                    if dn != dn_base:
                        # 将objectClass单独摘出来
                        l[index_new]["objectClass"] = object_class
                    else:
                        base_info["objectClass"] = object_class


            add_tree(res_tree)
    # raise ZeroDivisionError('心情不好')
    # print(res_tree)
    # return []
    base_info["children"] = res_tree
    res_tree_base = [base_info]

    return res_tree_base, res_dn_info


def error_format(msg):
    """
    将符合条件的ldap服务器报错翻译为中文并返回
    :param msg: ldap服务器的报错原文
    :return:
    """

    if msg == 'no structural object class provided':
        msg = "缺少结构化对象类(STRUCTURAL)"
    elif msg == 'noSuchObject':
        msg = '没有找到对应的域, 请创建后再查询'
    elif o := re.search(r"attribute '([^']*)' not allowed", msg):
        msg = f"不允许定义 '{o.group(1)}' 属性"
    elif o := re.search(r"([^:]*): value #([^ ]*) invalid per syntax", msg):
        msg = f"'{o.group(1)}' 属性的第 {int(o.group(2))+1} 个值的格式不对"
    elif o := re.search(r"value of naming attribute '([^']*)' is not present in entry", msg):
        msg = f"'{o.group(1)}' 属性缺少正确的值"
    elif o := re.search(r"value (.*) non valid for attribute '([^']*)'", msg):
        msg = f"'{o.group(2)}' 属性的值不能为 {o.group(1)}"
    elif o := re.search(r"value of single-valued naming attribute '([^']*)' conflicts with value present in entry", msg):
        msg = f"单值属性 {o.group(1)} 的值于dn中的命名属性值冲突 "
    return msg
