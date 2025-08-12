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

---

# 天津地铁5号线数据可视化界面

这是一个用于查看DXF转换后的GeoJSON数据的Web界面，支持地图显示、图层控制、文件搜索等功能。

## 🚀 快速开始

### 方法1：使用启动脚本（推荐）

```bash
cd dwg-to-dxf
python start_viewer.py
```

脚本会自动：
- 启动本地HTTP服务器（默认端口8000）
- 打开浏览器显示可视化界面
- 如果端口被占用，会自动尝试其他端口

### 方法2：手动启动

```bash
cd dwg-to-dxf
python -m http.server 8000
```

然后在浏览器中访问：`http://localhost:8000/viewer.html`

## 📁 文件结构

```
dwg-to-dxf/
├── viewer.html              # 主界面文件
├── start_viewer.py          # 启动脚本
├── extract_dxf_coords.py    # DXF转换脚本
├── tj_metro_lines/          # GeoJSON数据目录
│   ├── summary.geojson      # 汇总文件
│   ├── 车站地下_LINE_0001.geojson
│   ├── 车站地下_LINE_0002.geojson
│   └── ...
└── README.md                # 说明文档
```

## 🎯 功能特性

### 地图显示
- **底图切换**：街道地图 ↔ 卫星影像
- **坐标系统**：支持WGS84经纬度坐标
- **缩放平移**：鼠标滚轮缩放，拖拽平移

### 数据管理
- **文件列表**：显示所有GeoJSON文件
- **搜索功能**：快速查找特定文件
- **点击加载**：点击文件名将数据加载到地图

### 图层控制
- **显示/隐藏**：每个图层可独立控制
- **批量操作**：一键显示/隐藏所有图层
- **颜色区分**：不同图层使用不同颜色

### 交互功能
- **信息弹窗**：点击要素显示详细信息
- **适应视图**：自动调整地图范围
- **清空地图**：一键清除所有数据

## 🎨 界面说明

### 左侧边栏
- **标题区域**：显示项目名称和描述
- **搜索框**：快速搜索文件
- **文件列表**：所有可用的GeoJSON文件
- **控制面板**：图层控制、显示选项、地图操作

### 右侧地图
- **地图区域**：显示地理数据和底图
- **统计信息**：右上角显示数据统计
- **图例说明**：左下角显示颜色含义

## 🔧 使用说明

### 1. 查看数据
1. 启动服务器后，浏览器会自动打开界面
2. 在左侧文件列表中点击任意文件名
3. 数据会自动加载到地图上并显示

### 2. 图层控制
1. 在"图层控制"区域可以看到所有已加载的图层
2. 勾选/取消勾选复选框来控制图层显示
3. 使用"显示全部"/"隐藏全部"按钮进行批量操作

### 3. 地图操作
1. **适应视图**：自动调整地图范围以显示所有数据
2. **清空地图**：清除所有已加载的数据
3. **底图切换**：在地图右上角切换底图类型

### 4. 搜索文件
1. 在搜索框中输入关键词
2. 文件列表会实时过滤显示匹配的文件
3. 支持中文和英文搜索

## 🌐 技术架构

- **前端框架**：原生HTML/CSS/JavaScript
- **地图引擎**：Leaflet.js (开源地图库)
- **数据格式**：GeoJSON标准格式
- **服务器**：Python内置HTTP服务器

## 📊 数据格式

每个GeoJSON文件包含：
- **几何信息**：坐标点和几何类型
- **属性信息**：图层名、实体类型、颜色等
- **元数据**：文件来源、转换参数等

## 🚨 注意事项

1. **文件路径**：确保`tj_metro_lines`目录存在且包含GeoJSON文件
2. **坐标系统**：数据应为WGS84经纬度坐标，如果不是请先转换
3. **浏览器兼容**：建议使用Chrome、Firefox、Safari等现代浏览器
4. **网络访问**：如果需要在局域网内访问，请修改启动脚本中的IP地址

## 🔍 故障排除

### 问题1：无法启动服务器
- 检查端口是否被占用
- 确保有足够的权限
- 尝试使用其他端口

### 问题2：地图无法显示
- 检查网络连接（需要加载在线底图）
- 确认浏览器支持JavaScript
- 查看浏览器控制台错误信息

### 问题3：数据无法加载
- 确认GeoJSON文件路径正确
- 检查文件格式是否有效
- 查看浏览器网络请求状态

## 📞 技术支持

如果遇到问题，请检查：
1. 文件路径和权限
2. 网络连接状态
3. 浏览器控制台错误信息
4. Python版本兼容性

## 📝 更新日志

- **v1.0.0**：初始版本，支持基本的GeoJSON数据查看
- 支持线和面要素显示
- 提供图层控制和搜索功能
- 集成Leaflet地图引擎
