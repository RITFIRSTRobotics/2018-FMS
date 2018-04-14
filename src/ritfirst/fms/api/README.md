# FMSAPI
API for the Field Management System for Imagine RIT 2018

To deploy via Docker, run the following, starting from the root directory:

```
# build Docker container
docker build -t fmsapi ./

# run Docker container
docker run --name fmsapi -d -p 5000:5000 fmsapi
```

To stop and cleanup, use the following commands:
```
docker stop fmsapi
docker rm fmsapi
```
