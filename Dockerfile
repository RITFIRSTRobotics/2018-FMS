# Using lightweight alpine image
FROM python:3.6-alpine

# Installing packages
RUN apk update
RUN pip install --no-cache-dir pipenv

# Environment variables
ENV APP_ROOT=/usr/2018-fms/ API_SRC=/usr/2018-fms/src/ritfirst/fms/api/

# Defining working directory and adding source code
WORKDIR ${APP_ROOT}
COPY bootstrap.sh ./
COPY core ./core
COPY src ./src
WORKDIR ${API_SRC}

# Install API dependencies
RUN pipenv install

# Start app
EXPOSE 5000
ENTRYPOINT ${APP_ROOT}/bootstrap.sh
