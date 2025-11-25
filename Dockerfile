FROM python:3.11-slim

WORKDIR /app

# Set pip timeout and use mirror
RUN pip config set global.timeout 100
RUN pip config set global.retries 10

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

CMD ["python", "main.py"]