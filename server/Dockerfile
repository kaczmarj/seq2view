FROM python:3.8-slim
RUN useradd nonroot
WORKDIR /opt/server
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
USER nonroot
EXPOSE 5000
