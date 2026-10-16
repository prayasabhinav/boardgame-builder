# boardgameBuilder wiki for CapRover. The records live in /app/data, which must be a persistent volume.
FROM python:3.12-slim
WORKDIR /app
COPY wiki/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY corpus/ /corpus/
COPY wiki/ /app/
ENV HOST=0.0.0.0 PORT=80 CORPUS_DIR=/corpus DB_PATH=/app/data/wiki.db HTTPS_ONLY=1
EXPOSE 80
CMD ["python", "app.py"]
