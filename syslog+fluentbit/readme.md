# Distributed Log Aggregation using Syslog + Fluent Bit (Multi-Machine Setup)
This repository demonstrates a multi-host log aggregation system where microservices running on different machines send logs using the syslog protocol to a central machine where a log collector is running on a container, and centralized containers collect and forward logs across machines using fluent bit.

The setup uses:

Docker syslog logging driver

Fluent Bit as collector + forwarder

## Architecture
We are using four machines
```
        MACHINE-A                                MACHINE-B
  (Python Microservice)                      (C Microservice)
┌─────────────────────────┐            ┌─────────────────────────┐
│  Python Service         │            │  C Service              │
│  logger.info("msg")     │            │  syslog("msg")          │
└────────────┬────────────┘            └────────────┬────────────┘
             │                                      │
             │  Syslog over TCP                     │  Syslog over TCP
             │  (Docker logging driver)             │  (Docker logging driver)          
             │                                      │
             └──────────────────┬───────────────────┘
                                │
                                ▼
                            MACHINE-C(central machine)
              (Central Fluent Bit Collector + Forwarder)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive Syslog over TCP           │
          │  FILTER:  Parse / Enrich / Route logs       │
          │  BUFFER:  memory / disk                     │
          │  OUTPUT:  Forward via Syslog                │
          └─────────────────────┬───────────────────────┘
                                │
                                │  Syslog Forwarding
                                │
                                ▼
                            MACHINE-D
                  (Remote Fluent Bit Receiver)
          ┌─────────────────────────────────────────────┐
          │  INPUT:   Receive Syslog                    │
          │  STORE:   Elasticsearch / Loki / S3 / DB    │
          │  MONITOR: Grafana / Kibana / Dashboard      │
          └─────────────────────────────────────────────┘
```
### Key Principles

Applications log to stdout/stderr

Docker handles transport using the syslog protocol

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
For Machine-A code and configuration with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-python#) .


## Machine-B (C-Microservice)
For Machine-B code and configuration with the step by step process go to this [Link](https://github.com/DropletInk/log-aggregation-system/tree/micro-service-in-C) .

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
    Parsers_File    parsers.conf #Loads parser definitions

#defines how Fluent Bit receives logs.
[INPUT]
    Name            syslog
    Mode            tcp
    Listen          0.0.0.0
    Port            514 #should be the same port as the other micro-service's defined port
    Parser          syslog-rfc3164 #a syslog format 

# sending logs to stdout
[OUTPUT] 
    Name            stdout
    Match           *

# sending logs to a remote machine
[OUTPUT] 
    Name            forward
    Match           *
    Host            192.168.1.22 #remote machine's ip
    Port            5140 #remote machine's listening port
```
## docker-compose.yml
```docker
services:
  fluent-bit:
    image: fluent/fluent-bit:2.2
    container_name: fluent-bit-central
    ports:
      - "514:514"
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
    Name        forward
    Listen      0.0.0.0
    Port        5140
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
      - "5140:5140"
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
syslog as a logging driver is inductry standard. It is a very old standard used everywhere like linux server and containers. But it lacks some very important features or mechanisms like:

* It has limited retry capability.
* It does NOT buffer logs.