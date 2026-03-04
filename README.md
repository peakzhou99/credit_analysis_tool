APPID credit_analysis_tool

## 使用说明

生成对应的 pb2 和 pb2_grpc 文件。

```bash
python build_proto.py --proto-path /var/zgf/credit_analysis_tool/protos/credit_analysis_tool.proto
```




### 镜像制作

在 1.1.32.161 平台上使用如下命令制作镜像：

```bash
cd /var/zgf

git clone https://gitclone.com/github.com/peakzhou99/credit_analysis_tool.git

python build_image.py --name credit_analysis_tool --tag 1.3 --runner grpc \
    --grpc-app-path /var/zgf/credit_analysis_tool \
    --sub-dockerfile /var/zgf/credit_analysis_tool/Dockerfile
    
    
docker push harbordev.suningbank.com/llm/lwade-app/credit_analysis_tool:1.3
```

