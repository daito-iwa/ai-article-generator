FROM python:3.9-slim

WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 追加のWeb関連パッケージ
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    jinja2 \
    python-multipart

# アプリケーションコードをコピー
COPY . .

# 必要なディレクトリを作成
RUN mkdir -p data output logs static templates

# ポート設定
EXPOSE 8000

# アプリケーション起動
CMD ["python", "web_app.py"]