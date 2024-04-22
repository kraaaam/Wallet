FROM python:3.10.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Create and set the working directory
WORKDIR /app

# Install any dependencies
RUN apt update \
    && apt install -y \
    libpq-dev \
    build-essential \
    python3-dev

RUN pip3 install --upgrade pip
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



