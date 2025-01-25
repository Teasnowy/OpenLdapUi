import datetime
import logging
from flask import jsonify, request


def res_format(data=None, ok=None, err=None, code=None, jwt=None):
    """
    格式化后端生成的数据, 用来相应前端
    :param data: 正常返回的数据
    :param ok: 本次请求的状态, 正常应该是ok
    :param err: 错误信息, 可以为空
    :param code: 状态码, 正常为10000
    :param jwt: 当jwt被更新时, 将用此属性通知前端更新
    :return:
    """

    if err and not ok:
        # 如果有异常信息且没定义状态, 则赋值no
        ok = 'no'
    elif not ok:
        # 如果仅没定义状态, 则赋值ok
        ok = 'ok'

    # 如果err信息不为空,且code为空, 则code默认为10001
    if err and not code:
        code = 10001
    elif code:
        # 如果手动指定了code, 那么就用指定的值
        pass
    else:
        # 正常返回时code设定为10000
        code = 10000
    # logging.info(f"{type(data)}: {data}")

    # 如果发现data已被包装, 则不做动作

    # 返回格式为字典时的已包装判断
    # logging.info(f"被格式化的数据格式为: {type(data)}")
    if data and isinstance(data, dict):
        # logging.info(f"被格式化的数据key为: {list(data.keys())}")
        # logging.info(sorted(data.keys()))
        # logging.info(["code", "ok", "message_err", "data", "jwt", "time", ].sort())
        # 这里要注意列表内的元素的顺序, 与data_return中一致, 不然不会被判断一样
        if sorted(data.keys()) == sorted(["code", "ok", "message_err", "data", "jwt", "time", ]):
            logging.info(f"已被格式化, 返回原数据")
            return data

    # 返回格式为字符串时的已包装判断
    # try:
    #     json.loads(data)
    #     if list(data.keys()) == ["code", "ok", "message_err", "data", "time"]:
    #         return data
    # except Exception:
    #     pass

    data_return = {
        "code": code,
        "ok": ok,
        "message_err": err,
        "data": data,
        "jwt": jwt,
        "time": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    }

    # 这里依旧使用字符串, 因为用字典格式返回会导致raise ZeroDivisionError()无法被json序列化, 即使是flask的jsonify也不行
    # return json.dumps(data_return, default=str)
    # 这里又恢复了字典形式, 是因为接口处使用except ZeroDivisionError针对其单独做字符串
    return data_return


# 统一整理接口的各种try, 其中调用的函数必须只能接受data_request一个参数
def interface_try(func, request_input, is_jwt=True):
    """
    统一整理接口的各种try, 其中调用的函数必须只能接受data_request一个参数
    :param func: 处理数据的主函数
    :param request_input: 数据, 一般都是request
    :param is_jwt: 是否需要检查jwt
    :return:
    """
    url = request.url_rule.rule
    logging.info(f"当前请求的路径: {url}")

    try:
        data_json = request_input.json
        if not data_json:
            logging.error(f'{url}: POST报文为空, 已返回：Nothing to deal with')
            return res_format(err='POST报文为空'), 400
    except Exception as el:
        logging.error(f'{url}: POST报文格式必须为json, 数据:{request_input.data}')
        logging.exception(el)
        return res_format(err='POST报文格式必须为json'), 400
    logging.info(f"{url}: 收到报文: {data_json}")

    # 处理数据
    try:
        res_tmp = func(data_json)
        # logging.info(res)
        res = res_format(res_tmp)
        # logging.info(f"{url}: 返回: {res}")
        response = jsonify(res)
        # logging.info(f"返回的标头: {response.headers}")
        return response, 200
    except ZeroDivisionError as el:
        # 捕获 ZeroDivisionError 并提取错误信息
        res_el = res_format(err=str(el))
        logging.error(f"{url}: 返回报文: {res_el}")
        logging.exception(el)
        return res_el, 500
    except Exception as el:
        res_el = res_format(err=str(el))
        logging.error(f"{url}: 返回报文: {res_el}")
        logging.exception(el)
        return res_el, 500
