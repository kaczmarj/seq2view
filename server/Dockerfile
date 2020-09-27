FROM python:3.8-slim
WORKDIR /opt/server
ENV FLASK_APP="server.py" \
    FLASK_RUN_HOST="0.0.0.0"
RUN useradd nonroot
COPY requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY . .
USER nonroot
CMD ["flask", "run"]
