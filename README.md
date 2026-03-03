## 使用说明

生成对应的 pb2 和 pb2_grpc 文件。

```bash
python3 -m grpc_tools.protoc \
  -I ./protos \
  --python_out=./protos \
  --grpc_python_out=./protos \
  ./protos/credit_analysis_tool.proto
```

APPID = "credit_analysis_tool"

### 服务配置

在 config.py 中可以配置 APPID 以及服务端口和并发

```python

```


### 镜像制作

在 161 平台上使用如下命令制作镜像：

```bash
cd /var/zgf

git clone https://gitclone.com/github.com/peakzhou99/CreditAssistant.git

docker build -t harbordev.suningbank.com/llm/lmap/lmap-app-runner:CreditAssistant_v0.1 . \
--network host \
--build-arg HTTP_PROXY=http://10.0.34.5:18888 \
--build-arg HTTPS_PROXY=http://10.0.34.5:18888 \
--build-arg NO_PROXY='10.0.*.*.*,snb956101.com,*.suningbank.com'
```

