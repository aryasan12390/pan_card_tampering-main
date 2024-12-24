# FROM python:3.10
# WORKDIR /app
# COPY ./requirements.txt requirements.txt
# RUN pip install --no-cache-dir --upgrade -r requirements.txt
# COPY . .
# CMD ["gunicorn app:app"]

# Use the official Python image.
FROM python:3.10
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file first (to leverage Docker caching).
COPY ./requirements.txt /app/requirements.txt

# Install dependencies.
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application files.
COPY . /app

# Expose the port your application will run on (optional, for documentation).
EXPOSE 8000

# Default command to run your application.
CMD ["gunicorn", "app:app", "--workers=4", "--threads=2", "--bind=0.0.0.0:8000"]
