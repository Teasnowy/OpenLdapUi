# OpenLdapUi
openldap的可视化管理工具
![image](https://github.com/user-attachments/assets/3f349700-4577-4022-99a5-7c990809509a)

# 构成
- api目录: python (建议版本3.8+)
- web目录: vue3 + vite

# 自行编译
```
cd web
npm run build
mv dist web-dist
```

# 下载编译好的


# 运行环境
### 后端部分
```shell
pip install -r api/requeirments.txt
# 启动默认监听997端口, 如有需要可修改
python 
```
### 前端部分
依赖web服务器, 以下举例nginx
```
server  {
    listen       80;
    index index.html index.htm index.php;
    # 你手动编译或下载编译好的web目录
    root  /xxxx/web-dist;

    # /api是后端接口
    location /api {
        if ($request_method = 'OPTIONS') {
             return 200;
        }
        # 酌情修改997端口号
        proxy_pass   http://127.0.0.1:997;
        proxy_next_upstream off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
