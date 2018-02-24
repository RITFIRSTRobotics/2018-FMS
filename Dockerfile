# Using lightweight alpine image
FROM python:3.6-alpine

# Installing packages
RUN apk update
RUN pip install --no-cache-dir pipenv

# Defining working directory and adding source code
WORKDIR /usr/src/app
COPY ./src/ritfirst/fms/api/Pipfile ./src/ritfirst/fms/api/Pipfile.lock bootstrap.sh ./
COPY ./src/ritfirst/fms/api/fmsapi ./fmsapi

# Install API dependencies
RUN pipenv install

# Start app
EXPOSE 5000
ENTRYPOINT ["/usr/src/app/bootstrap.sh"]
