# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

COPY .env /app/.env
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the Streamlit app will run
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app2.py"]
