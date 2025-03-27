# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents (main.py, templates folder) into the container at /app
COPY . .

# Make port 9567 available to the host machine
EXPOSE 9567

# Run main.py when the container launches
# Use 0.0.0.0 to listen on all interfaces within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9567"]