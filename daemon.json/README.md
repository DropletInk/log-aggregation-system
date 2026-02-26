## Objective
Remove repetitive logging driver configuration in the docker-compsoe.yml for each service using daemon.json.
## Description
For every service we needed to specify the logging driver and its optional features in our docker-compose.yml file. For example:
```docker
  logging:
      driver: "fluentd"
      options:
        fluentd-address: "tcp://127.0.0.1:24224"
        tag: "service-a"
```
Also whenever a new serivce will be created we need to specify the same thing again and if any part is modified then we need to change the same modification in every place. 

To avoid or obliterate this issue we can configure the logging driver at the Docker Daemon level using the `daemon.json` file. After whenever a container will be up or even when a new container will be created the configuration of the `daemon.json` will be automatically attached to the container and w don't need to specify anymore.

## Step-By-Step Process

### check if the file exist in your system
 open terminal and write
```bash
ls -la /etc/docker/
```
This lists everything inside the `/etc/docker/` directory so you can see at a glance what's there.

### if it dosn't exist create the file
```
sudo mkdir /etc/docker/daemon.josn
```
### open the file in write mode
```
sudo nano /etc/docker/daemon.json
```
### write this into the file

```docker
{
  "log-driver":"fluentd",
  "log-opts":{
    "fluentd-address":"tcp://127.0.0.1:available_port"
    "tag": "{{.Name}}" #this tags the container name of the service automatically 
  }
}
```

### save the file
```
press ctr+o

then press Enter button
```
### Restart the docker
```bash
sudo systemctl restart docker
```
### Check if the docker is running
```bash
sudo systemctl status docker
```

## Result

### Before `docker-compose.yml` file

```docker
services:
  service-a:
    build: ./service-a
    container_name: service-a-local
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "tcp://127.0.0.1:24224"
        tag: "service-a"
  service-b:
    build: ./service-b
    container_name: service-b-local
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "tcp://127.0.0.1:24224"
        tag: "service-b"
  service-c:
    build: ./service-c
    container_name: service-c-local
    restart: always
    logging:
      driver: "fluentd"
      options:
         fluentd-address: "tcp://127.0.0.1:24224"
         tag: "service-c"
```

### After `docker-compose.yml` file

```docker
services:
  service-a:
    build: ./service-a
    container_name: service-a-local

  service-b:
    build: ./service-b
    container_name: service-b-local

  service-c:
    build: ./service-c
    container_name: service-c-local
    restart: always
```

