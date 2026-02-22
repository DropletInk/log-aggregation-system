# Distributed Log Aggregation using Syslog + Fluent Bit (Multi-Machine Setup)
This repository demonstrates a multi-host log aggregation system where microservices running on different machines send logs using the fluentd protocol to a central machine where a log collector is running on a container, and centralized containers collect and forward logs across machines using fluent bit.

The setup uses:

Docker fluentd logging driver

Fluent Bit as collector + forwarder

## Architecture
We are using four machines
```
        MACHINE-A                                MACHINE-B
  (Python Microservice)                      (C Microservice)
┌─────────────────────────┐            ┌─────────────────────────┐
│  Python Service         │            │       C Service         │   
└────────────┬────────────┘            └────────────┬────────────┘
             │                                      │
             │  fluentd over TCP                    │  fluentd over TCP
             │  (Docker logging driver)             │  (Docker logging driver)          
             │                                      │
             └──────────────────┬───────────────────┘
                                │
                                ▼
                            MACHINE-C(central machine)
              (Central Fluent Bit Collector + Forwarder)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive fluentd logs over TCP     │
          │  FILTER:  Parse / Enrich / Route logs       │
          │  BUFFER:  memory / disk                     │
          │  OUTPUT:  Forward via fluentd protocol      │
          └─────────────────────┬───────────────────────┘
                                │
                                │  Forwarding
                                │
                                ▼
                            MACHINE-D
                  (Remote Fluent Bit Receiver)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive fluentd logs              │
          │  STORE:   Elasticsearch / Loki / S3 / DB    │
          │  MONITOR: Grafana / Kibana / Dashboard      │
          └─────────────────────────────────────────────┘
```
### Key Principles

Applications log to stdout/stderr

Docker handles transport using the fluentd protocol

Fluent Bit acts as both:

* syslog receiver

* syslog relay

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
For Machine-A code with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-python#) . The docker-compose.yml is provide below

## docker-compose.yml
```docker
services:
  python-service:
    build: .
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "tcp://central-machine's ip:24220" #24220 is the listening port of the central machine
        tag: "python-service"
```

## Machine-B (C-Microservice)
For Machine-B code and configuration with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-C) . The docker-compose.yml is provided below

## docker-compose.yml
```docker
services:
  c-service:
    build: .
    logging:
      driver: "fluentd"
      options:
        fluentd-address: "tcp://central-machine's ip:24220"
        tag: "c-service"
```

## Machine-C (Central Collector + Forwarder)
Machine-C receives logs from A & B, then forwards to Machine-D.
### Folder structure
```
central-machine/
    ├── fluent-bit.conf
    └── docker-compose.yml
```
### fluent-bit.conf
```docker
#defines global settings that control how the Fluent Bit engine itself runs
[SERVICE] 
    Flush           1
    Daemon          Off
    Log_Level       info

#defines how Fluent Bit receives logs.
[INPUT]
    Name            forward
    Mode            tcp
    Listen          0.0.0.0
    Port            24220

# sending logs to stdout
[OUTPUT] 
    Name            stdout
    Match           *

# sending logs to a remote machine
[OUTPUT] 
    Name            remote
    Match           *
    Host            192.168.1.22 #remote machine's ip
    Port            24224 #remote machine's listening port
```
## docker-compose.yml
```docker
services:
  fluent-bit:
    image: fluent/fluent-bit:2.2
    container_name: fluent-bit-central
    ports:
      - "24220:24220"
    volumes:
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
    command: -c /fluent-bit/etc/fluent-bit.conf
    restart: always
```
## run
to run the container
```
docker compose up -d
```
to see all the logs coming from all micro-services
```
docker logs -f fluent-bit-central
```
## Machine-D (Remote Receiver Setup)

Machine-D is the final log destination.

### Folder Structure
```
remote-machine/
    ├── fluent-bit.conf
    └── docker-compose.yml
```
### fluent-bit.conf
```docker
[SERVICE]
    Flush        1
    Daemon       Off
    Log_Level    info

[INPUT]
    Name        remote
    Listen      0.0.0.0
    Port        24224
    Tag         remote.logs

[OUTPUT]
    Name   stdout
    Match  *
```
### docker-compose.yml
```docker
services:
  fluent-bit:
    image: fluent/fluent-bit:2.2
    container_name: fluent-bit-remote
    ports:
      - "24224:24224"
    volumes:
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
    restart: always

```
## run
to run the container
```
docker compose up -d
```
to see all the logs coming from all micro-services
```
docker logs -f fluent-bit-remote
```
## Observation
fluentd as logging driver is a good choice, it is widely used in projects and works perfectly with fluent-bit. 

**advantage**
* Direct structured log forwarding
* It supports buffering
* It supports retry on failure
* Real-time log streaming
* Centralized logging architecture friendly

**disadvantage**
* Higher CPU and memory usage
* complex configuration