# Use lightweight Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart pyarrow
# Copy only the necessary files and directories
COPY src/utils/feature/feature_extractor.py src/utils/feature/
COPY src/utils/inference/pose_inference.py src/utils/inference/
COPY src/weight/random_forest.pkl src/weight/
COPY src/__init__.py src/
COPY src/utils/__init__.py src/utils/

# Copy the FastAPI application main file
COPY app/ ./app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run FastAPI app with Uvicorn
CMD ["uvicorn", "app.application:app", "--host", "0.0.0.0", "--port", "8000"]
