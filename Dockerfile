# Use an official Python image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for uploads
RUN mkdir -p uploads/photos uploads/resumes

# Copy application code
COPY . .

# Copy the wait-for-it script
COPY scripts/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn with wait-for-it
CMD ["sh", "-c", "/usr/local/bin/wait-for-it.sh db:5432 -- uvicorn app.main:app --host 0.0.0.0 --port 8000"]