# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code and matrix file into the container
COPY app.py /app/
COPY S_mod.npy /app/
COPY movies.dat /app/
COPY blankUser.csv /app/

# Expose the port Flask runs on
EXPOSE 5000

# Define the command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]