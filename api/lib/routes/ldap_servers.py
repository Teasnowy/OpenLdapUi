# 程序自身运行情况监控或改变接口
import logging
import time
from flask import Blueprint, request
from ..data_format import interface_try
from ..ldapserver import conn, obj


ldap_servers = Blueprint('ldap_servers', __name__)


@ldap_servers.route('/api/devops/ldapserver/conn/getall', methods=['post'], endpoint="运维-LDAP-获取所有LDAP服务器")
def connect_get_all():
    """
    获取所有LDAP服务器
    """
    data_result = interface_try(conn.get_all, request, is_jwt=False)
    # time.sleep(2)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/conn/add', methods=['post'], endpoint="运维-LDAP-新增LDAP服务器")
def connect_add():
    """
    新增LDAP服务器
    """
    time.sleep(2)
    data_result = interface_try(conn.add, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/conn/update', methods=['post'], endpoint="运维-LDAP-更新一个LDAP服务器")
def connect_update():
    """
    更新一个LDAP服务器
    """
    time.sleep(2)
    data_result = interface_try(conn.update, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/conn/delete', methods=['post'], endpoint="运维-LDAP-删除一个LDAP服务器")
def connect_delete():
    """
    删除一个LDAP服务器
    """
    time.sleep(2)
    data_result = interface_try(conn.delete, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/getall', methods=['post'], endpoint="运维-LDAP-获取所有条目信息")
def object_getall():
    """
    获取所有条目信息
    """
    # time.sleep(2)
    data_result = interface_try(obj.get_all, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/add', methods=['post'], endpoint="运维-LDAP-创建一个dn")
def object_add():
    """
    创建一个dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.add, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/update', methods=['post'], endpoint="运维-LDAP-更新一个dn")
def object_update():
    """
    更新一个dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.update, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/move', methods=['post'], endpoint="运维-LDAP-移动一个dn")
def object_move():
    """
    移动一个dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.move, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/delete', methods=['post'], endpoint="运维-LDAP-批量删除dn")
def object_delete():
    """
    批量删除dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.delete, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/export', methods=['post'], endpoint="运维-LDAP-导出指定dn的ldif")
def object_export():
    """
    批量删除dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.export, request, is_jwt=False)
    return data_result


@ldap_servers.route('/api/devops/ldapserver/obj/upload', methods=['post'], endpoint="运维-LDAP-导入ldif")
def object_upload():
    """
    批量删除dn
    """
    # time.sleep(2)
    data_result = interface_try(obj.upload, request, is_jwt=False)
    return data_result