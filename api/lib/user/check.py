import re
import unicodedata


def get_custom_length(s: str) -> int:
    """
    计算字符串长度, 中文算2长度
    :param s:
    :return:
    """
    length = 0
    for char in s:
        # 判断字符是否为中文字符
        if unicodedata.category(char) == 'Lo':  # 'Lo' 是 Unicode 中的字母类，中文字符通常属于此类
            length += 2  # 中文字符视为两个字符
        else:
            length += 1  # 英文字符视为一个字符
    return length


def rule_account(user_account):
    """
    校验用户名格式
    :param user_account: 用户名
    :return:
    """

    # 必须是字符串
    if not isinstance(user_account, str):
        raise ZeroDivisionError(f"用户名必须是字符串格式")
    # 定义用户名和别名中允许包含的特殊字符
    nterpunction_user_list = ['_']
    # 判断用户名中是否包含不支持的特殊字符
    tmp_useraccount = re.sub('[a-zA-Z0-9]', '', user_account)
    for i in tmp_useraccount:
        if i not in nterpunction_user_list:
            raise ZeroDivisionError(f"用户名中仅允许包含特殊字符: {''.join(nterpunction_user_list)}")
    # 判断用户名位数是否超长
    if 4 > len(user_account) or len(user_account) > 30:
        raise ZeroDivisionError(f"用户名长度应在4至30字符之间")
    # logging.info(f"account{len(user_account)}通过")

def rule_displayname(user_displayname):
    """
    校验别名格式
    :param user_displayname: 别名
    :return:
    """

    # 必须是字符串
    if not isinstance(user_displayname, str):
        raise ZeroDivisionError(f"显示名必须是字符串格式")
    # 定义用户名和别名中允许包含的特殊字符
    nterpunction_user_list = ['-', '_']
    tmp_displayname = re.sub('[\u4e00-\u9fa5a-zA-Z0-9]', '', user_displayname)
    for i in tmp_displayname:
        if i not in nterpunction_user_list:
            raise ZeroDivisionError(f"显示名中仅允许包含特殊字符: {''.join(nterpunction_user_list)}")
    # 判断用户别名是否超长
    n = get_custom_length(user_displayname)

    if 4 > n or n > 30:
        raise ZeroDivisionError(f"名字长度应在4至30字符之间")


def rule_desc(desc, num_max:int=300, not_null=False):
    """
    校验详细描述信息
    :param desc:
    :param num_max: 最长支持多少字符, 默认300
    :param not_null: 是否不能为空, 默认为否
    :return:
    """

    if not_null and not desc:
        raise ZeroDivisionError(f"描述信息不允许为空")

    # 判断否超长
    n = get_custom_length(desc)

    if n > num_max:
        raise ZeroDivisionError(f"描述信息长度不能超过{num_max}")


def rule_url(url, num_max:int=300, not_null=True):
    """
    校验url
    :param url:
    :param num_max: 最长支持多少字符, 默认300
    :param not_null: 是否不能为空, 默认为否
    :return:
    """

    if not_null and not url:
        raise ZeroDivisionError(f"url不允许为空")

    # 判断否超长
    n = get_custom_length(url)

    if n > num_max:
        raise ZeroDivisionError(f"url长度不能超过{num_max}")



def rule_password(user_password):
    """
    校验密码格式
    :param user_password: 密码
    :return:
    """

    # 必须是字符串
    if not isinstance(user_password, str):
        raise ZeroDivisionError(f"密码必须是字符串格式")

    # 定义密码中允许包含的特殊字符
    nterpunction_passwd_list = '!@#$%^&*()_+-=,./?;:'
    if 30 < len(user_password) or len(user_password) < 6:
        raise ZeroDivisionError(f"密码长度应在6至30字符之间")
    # 判断密码中的特殊字符是否符合规定
    tmp_passwd = re.sub('[a-zA-Z0-9]', '', user_password)
    # logging.info(tmp_passwd)
    for i in tmp_passwd:
        if i not in nterpunction_passwd_list:
            raise ZeroDivisionError(f"密码中仅允许包含特殊字符: {''.join(nterpunction_passwd_list)}")
