FROM python:3.10-slim

WORKDIR /app

# Copy shared code
COPY shared/ /app/shared/

# Copy API service code
COPY api-service/ /app/api-service/

# Install Python dependencies
COPY api-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start the API service
CMD ["uvicorn", "api-service.main:app", "--host", "0.0.0.0", "--port", "8000"]
