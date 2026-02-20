# Micro-service in C language
This is a dummy micro-service written in C. It produces info level log.

## Logging driver
Here we have used syslog logging driver.
## syslog configuration in docker-compose.yml
```docker
logging:
    driver: "syslog"
    options:
      syslog-address: "tcp://192.168.1.19:514" #the ip address and the listening port of the central server should be the same as other microservices
      tag: "service-e" #optional but recommended
```
## Step by step process
### Step-1: build the image
```docker
docker compose build
```
### Step-2: run the container
```docker
docker compose up -d
```
### Step-3: See the logs
```docker
docker logs -f container_name
```
