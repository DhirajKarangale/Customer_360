FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . /app/backend

# Ensure Python can find the backend package
ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
