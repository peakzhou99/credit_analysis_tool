APPID credit_analysis_tool

## 使用说明

生成对应的 pb2 和 pb2_grpc 文件。

```bash

python3 -m grpc_tools.protoc \
  -I ./protos \
  --python_out=./protos \
  --grpc_python_out=./protos \
  ./protos/credit_analysis_tool.proto
  
  
python build_proto.py --proto-path /var/zgf/credit_analysis_tool/protos/credit_analysis_tool.proto
```




### 镜像制作

在 10.1.32.161 平台上使用如下命令制作镜像：

```bash
cd /var/zgf

git clone https://github.com/peakzhou99/credit_analysis_tool.git
备用：git clone https://gitclone.com/github.com/peakzhou99/credit_analysis_tool.git

cd /var/zgf/lwade_app_python-master

python build_image.py --name credit_analysis_tool --tag 1.9 --runner grpc \
    --grpc-app-path /var/zgf/credit_analysis_tool \
    --sub-dockerfile /var/zgf/credit_analysis_tool/Dockerfile
    
docker push harbordev.suningbank.com/llm/lwade-app/credit_analysis_tool:1.9
```

