FROM python:3.9-slim
WORKDIR /app
RUN pip install psycopg2-binary
COPY server.py .
CMD ["python", "-u", "server.py"]
