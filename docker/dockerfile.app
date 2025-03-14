# Use lightweight Python base image
FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/  
COPY app/ ./app/
COPY src/weight/* ./src/weight/
EXPOSE 8000

# Command to run FastAPI app with Uvicorn
CMD ["uvicorn", "app.application:app", "--host", "0.0.0.0", "--port", "8000"]
