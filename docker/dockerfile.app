# Use lightweight Python base image
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y unzip

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/  
COPY app/ ./app/
COPY src/weight/*.zip ./src/weight/


RUN unzip ./src/weight/*.zip -d ./src/weight/ && rm ./src/weight/*.zip

EXPOSE 8000

# Command to run FastAPI app with Uvicorn
CMD ["uvicorn", "app.application:app", "--host", "0.0.0.0", "--port", "8000"]
