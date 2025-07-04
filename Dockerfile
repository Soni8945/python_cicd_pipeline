# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# copy the dependency and install them
COPY requirement.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirement.txt
RUN pip install gunicorn

# Copy the current directory contents into the container at /app
COPY writtenby.py /app/
COPY config.ini .

# Run the Python script when the container starts
CMD ["gunicorn", "writtenby:app", "--bind", "0.0.0.0:5000", "--workers", "4"] 
