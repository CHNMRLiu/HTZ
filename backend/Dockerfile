FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN mkdir -p /app/data/uploads

EXPOSE 5671

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5671"]
