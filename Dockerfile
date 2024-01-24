FROM python:3.11-slim

# Set the working directory
WORKDIR /code

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
&& rm -rf /var/lib/apt/lists/*


# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8081"]
