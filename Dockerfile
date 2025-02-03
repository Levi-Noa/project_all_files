FROM python:3.9-slim

# Install Java (required for PySpark)
RUN apt-get update && apt-get install -y openjdk-17-jdk-headless && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y procps


# Copy the application files
COPY . .

# Run the pre_process.py script and then start the server
CMD ["sh", "-c", "python linkedin-about-generator/pre_process.py && python linkedin-about-generator/server.py"]