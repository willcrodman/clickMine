# Use Python 3.12.8 image
FROM python:3.12.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the contents from the currteent directory into the container
COPY . .

# Expose port 8080 (adjust as needed)
EXPOSE 8080

# Command to run the app
CMD ["python3", "app.py"]
