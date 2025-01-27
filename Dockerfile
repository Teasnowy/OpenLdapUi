# docker build --progress=plain -t openldapui:v1 .
FROM python:3.10.16-alpine3.21
# 安装nginx并设置开机启动
RUN apk add --no-cache nginx && ls /etc/nginx
# nginx配置文件
RUN echo 'server  {' > /etc/nginx/http.d/openldapui.conf && \
    echo '    listen       80;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    index index.html index.htm index.php;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    # 你手动编译或下载编译好的web目录' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    root  /openldapui/web-dist;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    # /api是后端接口' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    location /api {' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        if ($request_method = 'OPTIONS') {' >> /etc/nginx/http.d/openldapui.conf && \
    echo '             return 200;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        }' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        # 酌情修改997端口号' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        proxy_pass   http://127.0.0.1:997;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        proxy_next_upstream off;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        proxy_set_header Upgrade $http_upgrade;' >> /etc/nginx/http.d/openldapui.conf && \
    echo '        proxy_set_header Connection "upgrade";' >> /etc/nginx/http.d/openldapui.conf && \
    echo '    }' >> /etc/nginx/http.d/openldapui.conf && \
    echo '}' >> /etc/nginx/http.d/openldapui.conf
RUN rm -f /etc/nginx/http.d/default.conf
# 设定时区
RUN apk add --no-cache tzdata
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone && date
# 设置中文环境, musl库无需安装glibc
RUN apk add --no-cache musl-locales
# 这样设置/etc/profile似乎不起作用, 需要用ENV
RUN echo "export LANG=zh_CN.UTF-8" >> /etc/profile
RUN echo "export LC_ALL=zh_CN.UTF-8" >> /etc/profile && source /etc/profile
# 如果一切设置正确, 应该显示 zh_CN.UTF-8 等相关设置
# RUN localedef -i zh_CN -f UTF-8 zh_CN.UTF-8
ENV LANG=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8
RUN locale
# 安装python依赖
RUN pip install --no-cache-dir requests Flask ruamel.yaml ldap3 ldif
RUN pip cache purge
RUN mkdir /openldapui
# 拷贝前端文件
COPY OpenLdapUi/web-dist /openldapui/web-dist
# 拷贝后端文件
COPY OpenLdapUi/api /openldapui/api
# 设置启动相关
RUN echo "#!/bin/sh" > /openldapui/start.sh && \
    echo "# 启动 Nginx" >> /openldapui/start.sh && \
    echo "nginx -g 'daemon off;' &" >> /openldapui/start.sh && \
    echo "# 切换到指定目录并启动 Python API" >> /openldapui/start.sh && \
    echo "cd /openldapui/api && python OpenLdapUi-api.py" >> /openldapui/start.sh
RUN chmod +x /openldapui/start.sh
WORKDIR /openldapui
CMD ["/openldapui/start.sh"]
