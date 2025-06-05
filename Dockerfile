# Dockerfile for GCP AI Cost Optimizer Backend

FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app/backend/app

# Install system dependencies and gcloud CLI
RUN apt-get update && apt-get install -y gcc curl apt-transport-https ca-certificates gnupg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy backend code
COPY backend/app /app/backend/app

# Expose port
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008"]
