FROM ubuntu:22.04

# 安装依赖
RUN apt-get update && apt-get install -y \
    python3 python3-pip libfuse2 && \
    pip3 install flask

# 复制代码和 AppImage
WORKDIR /app
COPY app.py .
COPY ODAFileConverter.appimage /opt/ODAFileConverter.appimage
RUN chmod +x /opt/ODAFileConverter.appimage

EXPOSE 5000
CMD ["python3", "app.py"]