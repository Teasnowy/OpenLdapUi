from flask import Flask, request
import os
import logging
from lib.db.exec_ql import MysqlPool
# 引用自定义路由
from lib.routes.ldap_servers import ldap_servers


app = Flask(__name__)
# 注册蓝图
app.register_blueprint(ldap_servers)


@app.route('/ipput', endpoint="获取来访地址")
def index():
    # 获取来访地址
    ip = request.remote_addr
    with open('/app/ipupdate/data', 'w') as tmp:
        tmp.write(ip)
    return ip + '\n'


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(filename)s:%(funcName)s:%(thread)d:%(lineno)d %(message)s",
        encoding='utf-8'
    )

    mp = MysqlPool()
    mp.connect()
    mp.transaction("""
        create table IF NOT EXISTS `sw_ldap_servers` (
          `server_name` varchar(30) NOT NULL ,
          `server_addr` varchar(200) NOT NULL,
          `server_base` varchar(200) NOT NULL,
          `server_auth_dn` varchar(200) NOT NULL,
          `server_auth_passwd` varchar(200) NOT NULL,
          `date_create` datetime NOT NULL,
          `date_update` datetime NOT NULL,
          PRIMARY KEY (`server_name`)
        );
    """)

    # 获取脚本所在路径
    # dir_app = os.path.dirname(sys.argv[0])
    dir_app = os.path.dirname(os.path.abspath(__file__))
    # 进入脚本所在路径
    os.chdir(dir_app)

    app.run(host="0.0.0.0", port=997)




