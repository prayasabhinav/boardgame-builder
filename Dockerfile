# boardgame for CapRover: Python, no build step, nothing written to disk, no model and no key.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY VERSION *.py interactions.json interactions-drafted.json block-questions.json part-tests.json games.json ./
COPY static/ static/
ENV HOST=0.0.0.0 PORT=80
EXPOSE 80
CMD ["python", "app.py"]
