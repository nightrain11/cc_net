FROM python:3.7
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y make
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y cmake
WORKDIR ./ccnet
VOLUME ./:/~/repo
ADD . .
CMD []

#docker编译Dockerfile文件
#sudo docker build -t ccnet:1.0 .

#docker 创建后台容器
#sudo docker run -itd --name container(自定义) -p 8888:8888 cc_net:1.0(images名称) /bin/bash

# -v 将宿主机的/test目录挂载在容器的/soft目录，/soft目录会在容器创建时自动创建。容器内路径为绝对路径，以/开头。
#sudo docker run -itd --name=container -v /test:/soft cc_net:1.0 /bin/bash

#sudo docker run -itd --name=cc_net_container -v /home/mobvoi/gitRepo/cc_net/data:/data -v /home/mobvoi/gitRepo/cc_net:/ccnet -p 8888:8888 cc_net:1.0 /bin/bash

#docker 退出
#exit

#docker 重入
#docker exec -it imageID /bin/bash

#docker 迁移
#docker commit [containerID] [imageName]:[version](自定义)
#docker save -o ~/cc_net.tar cc_net:1.0
#docker load -i ~/cc_net.tar

#docker重新命名images
#docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG] 重新命名docker

#docker文件copy
#docker cp containerId:文件路径 容器外需存放路径

#启动容器
#docker start 容器名称

#停止容器
#docker stop 容器名称

#查看容器的相关详情
#docker inspect

#sudo scp -i ~/.ssh/chuangwang ./cc-net-test:1.0  chuangwang@42.192.20.81:~

