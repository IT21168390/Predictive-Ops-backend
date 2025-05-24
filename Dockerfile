FROM python:3.12.10-slim

# ---- system ---------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# ---- python ---------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- code -----------------------------------------------------------------
COPY . .

# Ensure the key directory exists and create a placeholder file
# This prevents Docker from creating the mount point as a directory
RUN mkdir -p /app/preprocessor/key && \
    touch /app/preprocessor/key/predictivemaintenancesystem-firebase-adminsdk-w2tny-15b2aec14c.json

# FastAPI listens on :8000
EXPOSE 8000

# CMD ["python", "-m", "preprocessor.main"]

# Change this line - run main.py directly from the preprocessor directory
CMD ["python", "preprocessor/main.py"]