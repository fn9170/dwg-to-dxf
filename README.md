# DWG转DXF格式转换服务 | DWG to DXF Converter Service

[中文](#中文) | [English](#english)

---

## 中文

### 概述

一个用于将AutoCAD DWG文件转换为DXF格式的容器化微服务。该服务提供简单的REST API端点，接受DWG文件并使用ODA File Converter返回转换后的DXF文件。

### 功能特性

- **RESTful API**: 简单的HTTP POST端点进行文件转换
- **容器化**: Docker就绪，便于部署和扩展
- **格式支持**: 将DWG文件转换为DXF R2013格式
- **错误处理**: 全面的错误处理和验证
- **无状态**: 无持久化存储，完美适配微服务架构

### 技术栈

- **后端**: Python Flask
- **转换引擎**: ODA File Converter (AppImage)
- **容器**: Docker with Ubuntu 22.04
- **API**: RESTful HTTP API

### 快速开始

#### 前置要求

- 系统已安装Docker
- ODA File Converter AppImage（放置在项目根目录，命名为 `ODAFileConverter.appimage`）

#### 构建和运行

```bash
# 克隆仓库
git clone <repository-url>
cd dwg-to-dxf

# 构建Docker镜像
docker build -t dwg-to-dxf .

# 运行容器
docker run -p 5000:5000 dwg-to-dxf
```

#### API使用方法

**端点**: `POST /convert`

**请求**:

- 方法: POST
- Content-Type: multipart/form-data
- 请求体: DWG文件，键名为"file"

**响应**:

- 成功: DXF文件下载
- 错误: JSON错误消息

**使用curl示例**:

```bash
curl -X POST -F "file=@example.dwg" http://localhost:5000/convert -o output.dxf
```

**API测试示例**:

![API使用示例](image/README/1754549286722.png)

**使用Python示例**:

```python
import requests

with open('example.dwg', 'rb') as f:
    response = requests.post('http://localhost:5000/convert', files={'file': f})
  
if response.status_code == 200:
    with open('output.dxf', 'wb') as out:
        out.write(response.content)
else:
    print(f"错误: {response.json()}")
```

### 部署方式

#### Docker Compose

```yaml
version: '3.8'
services:
  dwg-converter:
    build: .
    ports:
      - "5000:5000"
    restart: unless-stopped
```

#### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwg-converter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dwg-converter
  template:
    metadata:
      labels:
        app: dwg-converter
    spec:
      containers:
      - name: dwg-converter
        image: dwg-to-dxf:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: dwg-converter-service
spec:
  selector:
    app: dwg-converter
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### 错误代码

| 状态码 | 描述                              |
| ------ | --------------------------------- |
| 200    | 成功 - 返回DXF文件                |
| 400    | 请求错误 - 无效文件格式或缺少文件 |
| 500    | 内部服务器错误 - 转换失败         |

### 安全注意事项

⚠️ **重要安全提示**: 本平台/本系统为互联网非涉密平台，**严禁处理传输国家秘密**。

### 许可证

详情请参见 [LICENSE](LICENSE) 文件。

---

## English

### Overview

A containerized microservice for converting AutoCAD DWG files to DXF format. This service provides a simple REST API endpoint that accepts DWG files and returns converted DXF files using the ODA File Converter.

### Features

- **RESTful API**: Simple HTTP POST endpoint for file conversion
- **Containerized**: Docker-ready for easy deployment and scaling
- **Format Support**: Converts DWG files to DXF R2013 format
- **Error Handling**: Comprehensive error handling and validation
- **Stateless**: No persistent storage, perfect for microservice architecture

### Technology Stack

- **Backend**: Python Flask
- **Converter Engine**: ODA File Converter (AppImage)
- **Container**: Docker with Ubuntu 22.04
- **API**: RESTful HTTP API

### Quick Start

#### Prerequisites

- Docker installed on your system
- ODA File Converter AppImage (place in project root as `ODAFileConverter.appimage`)

#### Build and Run

```bash
# Clone the repository
git clone <repository-url>
cd dwg-to-dxf

# Build Docker image
docker build -t dwg-to-dxf .

# Run container
docker run -p 5000:5000 dwg-to-dxf
```

#### API Usage

**Endpoint**: `POST /convert`

**Request**:

- Method: POST
- Content-Type: multipart/form-data
- Body: DWG file with key "file"

**Response**:

- Success: DXF file download
- Error: JSON error message

**Example using curl**:

```bash
curl -X POST -F "file=@example.dwg" http://localhost:5000/convert -o output.dxf
```

**Example using Python**:

```python
import requests

with open('example.dwg', 'rb') as f:
    response = requests.post('http://localhost:5000/convert', files={'file': f})
  
if response.status_code == 200:
    with open('output.dxf', 'wb') as out:
        out.write(response.content)
else:
    print(f"Error: {response.json()}")
```

### Deployment

#### Docker Compose

```yaml
version: '3.8'
services:
  dwg-converter:
    build: .
    ports:
      - "5000:5000"
    restart: unless-stopped
```

#### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwg-converter
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dwg-converter
  template:
    metadata:
      labels:
        app: dwg-converter
    spec:
      containers:
      - name: dwg-converter
        image: dwg-to-dxf:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: dwg-converter-service
spec:
  selector:
    app: dwg-converter
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Error Codes

| Status Code | Description                                       |
| ----------- | ------------------------------------------------- |
| 200         | Success - DXF file returned                       |
| 400         | Bad Request - Invalid file format or missing file |
| 500         | Internal Server Error - Conversion failed         |

### Security Considerations

⚠️ **Important Security Notice**: This platform is designed for non-confidential internet use only. **Strictly prohibited from processing or transmitting state secrets.**

### License

See [LICENSE](LICENSE) file for details.
