# Sử dụng một image Python chính thức từ Docker Hub
FROM python:3.10-slim

# Đặt biến môi trường để ngăn chặn việc tạo ra các tệp .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tạo một thư mục làm việc trong container
WORKDIR /app

ENV SCRIPT_DIR="/app"
ENV RAW_DATA_DIR="$SCRIPT_DIR/data/raw"
ENV PROCESS_DATA_DIR="$SCRIPT_DIR/data/processed"
ENV INTERMEDIATE_DATA_DIR="$SCRIPT_DIR/data/interim"
ENV REFS_DIR="$SCRIPT_DIR/references"
ENV MOSSES_DECODER="$SCRIPT_DIR/references/mossesdecoder"
ENV MODELS_DIR="$SCRIPT_DIR/models"
ENV PYTHONPATH="/app/src"


# Sao chép file yêu cầu vào thư mục làm việc
COPY requirements.txt /app/

# Cài đặt các dependencies
# Cập nhật hệ thống và cài đặt các công cụ cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-pip \
    python3-dev \
    git \
    curl \
    iputils-ping \
    nano \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --default-timeout=1000 -r requirements.txt
# RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*
# Cập nhật gói và cài đặt curl và ping
# RUN apt update && apt install -y curl iputils-ping nano

# Sao chép toàn bộ mã nguồn 
COPY run.py /app/
COPY setEnv.sh /app/
COPY src/ /app/src
COPY references/ /app/references

# Mở cổng 8000 cho Uvicorn
EXPOSE 8000
# Mở cổng 8501 cho streamlit
EXPOSE 8501

# Lệnh để chạy ứng dụng của bạn (thay đổi tuỳ theo ứng dụng của bạn)
ENTRYPOINT ["python3", "/app/run.py"]
# CMD ["python3", "/app/run.py"]
# ENTRYPOINT ["streamlit", "run", "run.py", "--server.port=8501", "--server.address=0.0.0.0"]
