FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Render provides PORT environment variable automatically
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Start the server (change main:app if different)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
