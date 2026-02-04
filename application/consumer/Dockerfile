FROM python:3.11-slim
WORKDIR /app
COPY consumer.py .
RUN pip install redis pika
CMD ["python", "consumer.py"]
