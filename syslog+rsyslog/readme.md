# Distributed Log Aggregation using Syslog + Fluent Bit (Multi-Machine Setup)
This experiment demonstrates a centralized logging architecture where microservices running on multiple machines send logs using the syslog protocol, which are collected by a central rsyslog container and then forwarded to a remote machine using remote-syslog forwarding.

The setup uses:

Docker syslog logging driver

rsyslog as collector + forwarder

## Short Description
### syslog
syslog is a docker logging driver. It is a standardized protocol which is used to send logs accross systems.

**Key Features**

* It works over tcp/udp connection
* It supports structured message format
* Supports priority levels.

### rsyslog(Rocker-fast system for log processing)
rsyslog is a high-performance syslog server used for recieving logs, processing, storing and forwarding.

### remote-syslog
remote-syslog is the process of sending logs from one machine to another over the network.

## Architecture
We are using four machines
```
        MACHINE-A                                MACHINE-B
  (Python Microservice)                      (C Microservice)
┌─────────────────────────┐            ┌─────────────────────────┐
│  Python Service         │            │  C Service              │         
└────────────┬────────────┘            └────────────┬────────────┘
             │                                      │
             │  Syslog over TCP                     │  Syslog over TCP
             │  (Docker logging driver)             │  (Docker logging driver)          
             │                                      │
             └──────────────────┬───────────────────┘
                                │
                                ▼
                     MACHINE-C(central machine)
                  (rsyslog Collector + Forwarder)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive syslog over TCP           │
          │  FILTER:  Parse / Enrich / Route logs       │
          │  STORE:   /var/log/central/*.log            │
          │  OUTPUT:  Forward via Syslog to remote      │
          └─────────────────────┬───────────────────────┘
                                │
                                │  Syslog Forwarding
                                │
                                ▼
                            MACHINE-D
                  (Remote rsyslog Receiver)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive Syslog over TCP           │
          │  STORE:   /var/log/remote/*.log             │
          │  MONITOR: Grafana / Kibana / Dashboard      │
          └─────────────────────────────────────────────┘
```
### Key Principles

Applications log to stdout/stderr

Docker handles transport using the syslog protocol

rsyslog acts as both:

* syslog receiver

* syslog forwarder

## Prerequisites

Install Docker on all machines:
```
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```
### How Log Flow Works

## Machine-A (python Microservice)
For Machine-A code and configuration with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-python#) .


## Machine-B (C-Microservice)
For Machine-B code and configuration with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-C) .

## Machine-C (Central Collector + Forwarder)
Machine-C receives logs from A & B, then forwards to Machine-D.
### Folder structure
```
 📁central-machine
    └── 📁rsyslog
        ├── Dockerfile
        ├── rsyslog.conf
    └── docker-compose.yml
```
### rsyslog.conf
```docker
module(load="imudp") #load the upd module
input(type="imudp" port="5141") #any system sending logs via UDP to this machine on port 5141 will be received

module(load="imtcp") #load the tcp module
input(type="imtcp" port="5141") #any system sending logs via tcp to this machine on port 5141 will be received

#optional: define a template for log storage, it automatically stores logs in a folder defined here  
template(name="RemoteLogs" type="string"
 string="/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log") #log file path format

*.* ?RemoteLogs #use template named RemoteLogs to save all logs

*.* /dev/stdout #send all logs to stdout

*.* @@192.168.1.22:5144 #forward all logs to another remote machine using TCP

# @ -> for udp
# @@ -> for tcp
```

## Dockerfile
```docker
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y rsyslog iproute2 net-tools
COPY rsyslog.conf /etc/rsyslog.conf
CMD ["rsyslogd", "-n"]
```

## docker-compose.yml
```docker
services:
  central-rsyslog:
    build: ./rsyslog
    container_name: central-rsyslog
    ports:
      - "5141:5141/udp"
      - "5141:5141/tcp"
    volumes:
      - ./remote-logs:/var/log/remote
    restart: always
```
## run
1. Build the image
```docker
docker compose build
```

2. run the container
```
docker compose up -d
```
3. to see all the logs coming from all micro-services
```
docker logs -f central-rsyslog
```
## Machine-D (Remote Receiver Setup)

Machine-D is the final log destination.

### Folder Structure
```
└── 📁remote-machine
    └── 📁rsyslog
        ├── Dockerfile
        ├── rsyslog.conf
    └── docker-compose.yml
```
### rsyslog.conf
```docker
module(load="imudp")
input(type="imudp" port="5144")

module(load="imtcp")
input(type="imtcp" port="5144")

*.* /dev/stdout
```

### Dockerfile
```docker
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y rsyslog iproute2 net-tools
COPY rsyslog.conf /etc/rsyslog.conf
CMD ["rsyslogd", "-n"]
```
### docker-compose.yml
```docker
services:
  central-rsyslog:
    build: ./rsyslog
    container_name: remote-rsyslog
    ports:
      - "5144:5144/udp"
      - "5144:5144/tcp"
    volumes:
      - ./remote-logs:/var/log/remote
    restart: always
```
## step by step process

1. Build the image
```terminal
docker compose build
```
2. run the container
```
docker compose up -d
```
3. to see all the logs coming from all micro-services
```
docker logs -f remote-rsyslog
```
## Observation
syslog as a logging driver is inductry standard. It is a very old standard used everywhere like linux server and containers. But it lacks some very important features or mechanisms like:

* It has limited retry capability.
* It does NOT buffer logs.

Since rsyslog works on syslog protocol it can only be used with syslog logging driver which limits our options. 