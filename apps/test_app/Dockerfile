FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask boto3

# Copy application
COPY app.py /app/app.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()"

# Run application
CMD ["python", "-u", "app.py"]
