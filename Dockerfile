# Builder image
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /code

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libgl1-mesa-glx \
&& rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11-slim

# Set the working directory
WORKDIR /code

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the rest of the application code
COPY . .

# Run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8081"]
