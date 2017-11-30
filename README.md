## api-buluprint:
    md文件生成html =======> aglio -i pim_api_buleprint.md -o pim_api_buleprint.html


## docker 部署简便步骤:
    1.docker build -t pim_api .  # **本地build镜像**
    2.docker run -p 6666:5000 pim_api # **本地run个端口号**
    3.docker push pim_api # push至gitlab # **本地push项目镜像**
    4. docker login registry.gitlab.com # **线上登录**
        4.1 docker build -t registry.gitlab.com/hsbs/weberp/pim_api . # **在线上build** (可忽略)
        4.2 docker push registry.gitlab.com/hsbs/weberp/pim_api # **在线上push项目镜像** (可忽略)
        4.3 docker pull registry.gitlab.com/hsbs/weberp/pim_api:dev # **在线上pull项目镜像**
    5. docker ps # 列出所有运行中的容器, -a 列出所有容器（含沉睡镜像）(可忽略)
    6. docker images # 列出所有镜像
    7. docker logs (NAMES: elegant_austin)# 打印容器日志
    8. docker stop (CONTAINER ID: 360840e26b43)# 停止容器进程
       docker rmi xxx (IMAGE ID: a2459c4d3215)   # 删除一个docker容器镜像
       docker tag xxxx xxx v0.5 # 镜像打个版本
    9. docker run --name pimpostgre -e POSTGRES_PASSWORD=123456
        -e POSTGRES_USER=jim -d -p 50302:5432 postgres
        # 数据库配置
    10. docker run -p 30305:5000  -e "PG_USER=jim"
        -e "MIGRATE=1" -e "PG_PWD=123456" -e "PG_HOST=47.100.21.215"
        -e "PG_PORT=50310" -e "PG_DB=pim" -d registry.gitlab.com/hsbs/weberp/pim_api:v0.5
        # 配置容器环境变量并运行容器程序