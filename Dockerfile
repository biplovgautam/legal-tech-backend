# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies (if needed for psycopg2 or others)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Render will ignore this but good for documentation)
EXPOSE 8000

# Run the application
# We use the shell form to allow variable expansion for PORT if needed, 
# but since we are using run.py which uses Pydantic Settings to read PORT env var,
# we can just run the script.
# We also run create_tables.py before starting the app to ensure DB schema exists.
CMD python create_tables.py && python run.py
