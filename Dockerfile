# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Set the environment variable to tell Flask it's in production
ENV FLASK_ENV=production

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the application (assuming your app is named `app.py` and Flask instance is `app`)
CMD ["gunicorn", "app:app"]
