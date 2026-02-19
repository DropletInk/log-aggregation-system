## Aggregate logs from different microservices running in different containers in different machines into a central machine's container where we can manage the logs and send the logs somewhere else(another machine, LOKI etc.)
 **What are the logs?** 

Logs are automatically generated files that record chronological events, activities, and messages occurring within an operating system, application, or network device. They are like a “digital logbook” that stores timestamps, user actions, system errors, and security events for troubleshooting, debugging, and compliance. 

**What is logging?**

It is the process of recording events that happen inside a software system over time. These events are written as log messages. 

**What exactly gets logged?** 

Application logs such as:  

  . Application start/stop 

  . API requests and responses 

  . Errors and exceptions 

  . Database queries 

  . uthentication attempts 

  . Performance timing 
  
**Example:**  

2026-02-03 10:15:32  |    INFO   |  user service  | – user login successful (user I'd = 42) 

## **Logging Levels:** 

1. OFF   ->   Do not create a log.
2. FATAL ->  include fatal statements / very severe error (events that will presumably lead the application to abort/terminate. 
3. ERROR ->  something broke but the system is still running. 
4. WARN  ->  Potentially harmful situations or when something looks off but is still working. 
5. INFO  ->  informational messages that highlight the progress of the application at coarse-grained level. 
6. DEBUG ->  Diagnostic information used for debugging. 
7. ALL   ->  Include all levels of information in the log. 
8. TRACE ->  More detailed information about the flow of the system. 
## Different Logging Drivers 
**What are Logging Drivers?** 

It is the component responsible for capturing container stdout/stderr(standard input, output, errors of the system) logs and deciding where & how these logs are stored or forwarded. 

``Application -> stdout/stderr -> docker runtime intercepts them -> Docker logging driver handles them``

### 1. json-file: By default, driver in Docker, writes logs as JSON files on the host. 

**Pros:** 

. Default (no config needed) 

. Works everywhere 

. Supports log rotation (log rotation: when a log file hits a size or time limit, it is renamed, often compressed, and a new file is created to continue logging). 

. Compatible with all collectors 

**Cons:**

. Stored in local storage, disk usage issue 

. No built-in forwarding 

. Host-dependent paths

### 2. journald (Host-centric) : 

Sends logs to systemd journal. systemd is the default system and service manager for most modern Linux distribution. It is a part of systemd. 

Collects logs from:  system services, kernel, Docker containers, stdout/stderr of processes, Stores logs in a binary journal, We don’t need to install it — it already exists on most Linux distros. 

**Pros:** 

. Centralized host logging 

. Built-in indexing and rotation 

. Metadata (unit, PID, container ID) 

**Cons:**

. Requires systemd 

. Needs privileged access 

. Not portable across OS 

. Logs cannot be forwarded  

**How journald works:**
1. Services write to stdout/stderr 

2. journald captures log message, service name, PID, UID, container name, timestamps 

3. Then logs are queried using: journalctl 

Example: journalctl CONTAINER_NAME=service-a -f 

``Log flow: Container -> journald -> journalctl`` 

### 3. syslog (Network Forwarding): 

Syslog is a standard protocol for message logging, allowing network devices, servers, and applications to generate, store, and analyze event logs centrally. 

. Sends logs to a syslog server 

. Uses TCP/UDP 

``Log flow: Container -> syslog -> log server`` 

**Pros:** 

. Simple & standardized 

. Remote shipping 

. Works with rsyslog / syslog-ng 

**Cons:** 

. UDP can drop logs 

. TCP can block containers 

. Docker blocks if syslog is slow 

 ### 4. fluentd (collector-friendly): 
 
 A log aggregation and forwarding platform, Written in Ruby, heavy, powerful, extremely flexible 

Acts as: collector, processor, router, shipper 

``Log flow: INPUT -> PARSER -> FILTER -> FILTER -> OUTPUT``

**Pros:** 
. Centralized logging: Aggregates logs from many nodes 

. Powerful processing: Parsing, Enrichment, Filtering, Conditional routing 

. Huge plugin ecosystem: 1000+ plugins, almost any input/output imaginable 

. Production-proven: Used at large scale (K8s, cloud providers) 

**Cons:**  

. Heavy, high memory & CPU usage 

. Operational complexity 

. Overkill for simple use cases 

### Other logging drivers

There are other logging drivers like: 

**none** - No logs are available for the container and docker logs does not return any output.

**local** - Logs are stored in a custom format designed for minimal overhead.

**gelf** - Writes log messages to a Graylog Extended Log Format (GELF) endpoint such as Graylog or Logstash.

**awslogs** - Writes log messages to Amazon CloudWatch Logs.

**splunk** - Writes log messages to splunk using the HTTP Event Collector.

**etwlogs** - Writes log messages as Event Tracing for Windows (ETW) events. Only available on Windows platforms.

**gcplogs** - Writes log messages to Google Cloud Platform (GCP) Logging.

## Log Aggregation Process
**What is Log Aggregation?**

Log aggregation is the process of collecting logs from multiple services, machines, or containers and storing them in a single, centralized location for monitoring, debugging, and analysis.

Now there are basically two ways to aggregate the logs in a central machine:

**1. Setup local logging agent in each machine where the microserices are running**
   
**2. Without using a local logging agent**

### Process -1 : Using a local logging agent
**What is local logging agent?**

A local logging agent is a small program that runs on each machine and is responsible for collecting logs locally, processing them, and forwarding them to a central logging system. Think of it as a log collector and forwarder installed on each machine.

**Example:**

. Fluent Bit (lightweight, most popular)

. Fluentd (heavier, more powerful)

. Logstash

. rsyslog

**What the Local Logging Agent Actually Does?**

it performs four main task:
**1. Collect logs** - Reads logs from Docker containers, Files, journald, syslog and stdou/stderr

**2. Parse logs** - Converts raw logs into structured format.

**3. Buffer logs** - If the central server or machine is down 

a. Without agent logs might be lost 

b. with agent logs are buffered and can be sent later

**4. Forward logs to central server** - Sends logs to Grafana Loki, Elasticsearch, Remote machine.

### Architecture
```
┌─────────────────────────────────────┐      ┌─────────────────────────────────────┐
│             MACHINE 1               │      │             MACHINE 2               │
│                                     │      │                                     │
│  ┌─────────────────────────────┐    │      │  ┌─────────────────────────────┐    │
│  │  Python Microservice        │    │      │  │  Node.js Microservice       │    │
│  │  (Docker Container)         │    │      │  │  (Docker Container)         │    │
│  └──────────────┬──────────────┘    │      │  └──────────────┬──────────────┘    │
│                 │ stdout/stderr     │      │                 │ stdout/stderr     │
│                 ▼                   │      │                 ▼                   │
│  ┌─────────────────────────────┐    │      │  ┌─────────────────────────────┐    │
│  │  Docker Logging Driver      │    │      │  │  Docker Logging Driver      │    │
│  │                             │    │      │  │                             │    │
│  └──────────────┬──────────────┘    │      │  └──────────────┬──────────────┘    │
│                 │                   │      │                 │                   │
│                 ▼                   │      │                 ▼                   │
│  /var/lib/docker/containers/*.log   │      │  /var/lib/docker/containers/*.log   │
│                 │                   │      │                 │                   │
│                 ▼                   │      │                 ▼                   │
│  ┌─────────────────────────────┐    │      │  ┌─────────────────────────────┐    │
│  │    Local logging Agent      │    │      │  │    Local logging Agent      │    │
│  │  - INPUT:   tail logs       │    │      │  │  - INPUT:   tail logs       │    │ 
│  │  - PARSE:   structured logs │    │      │  │  - PARSE:   structured logs │    │
│  │  - BUFFER:  memory/disk     │    │      │  │  - BUFFER:  memory/disk     │    │
│  │  - FORWARD: central server  │    │      │  │  - FORWARD: central server  │    │
│  └──────────────┬──────────────┘    │      │  └──────────────┬──────────────┘    │
└─────────────────┼───────────────────┘      └─────────────────┼───────────────────┘
                  │                                            │
                  │                Forward logs                │
                  └─────────────────────┬──────────────────────┘
                                        │
                                        ▼
               ┌────────────────────────────────────────────┐
               │          CENTRAL LOGGING MACHINE           │
               │                                            │
               │   ┌────────────────────────────────────┐   │
               │   │  Central Fluent Bit (Aggregator)   │   │
               │   │  - INPUT:  receive from agents     │   │
               │   │  - FILTER: enrich / modify logs    │   │
               │   │  - ROUTE:  by service / level      │   │
               │   │  - OUTPUT: forward to remote       │   │
               │   └──────────────────┬─────────────────┘   │
               └──────────────────────┼─────────────────────┘
                                      │
                                      │  TCP / HTTPS / Syslog
                                      │
                                      ▼
               ┌────────────────────────────────────────────┐
               │             REMOTE SERVER                  │
               │                                            │
               │          Log Storage & Analysis            │
               │       (Remote machine / Grafana Loki /     │
               │             Elasticsearch / S3)            │
               └────────────────────────────────────────────┘
```

**Step-by-Step Flow Explanation**

#### Step 1: Application generates logs

for example:

Python service:
```python
logger.info("User logged in")
```
Node.js service:
```node.js
console.log("API request received")
```
These go to:
```
stdout / stderr
```
#### Step 2: Docker captures stdout/stderr

Docker automatically captures both streams

#### Step 3: Local Logging Agent collects logs

Local logging agent runs on each machine. It reads Docker log files.

#### Step 4: Local agent buffers logs

If central server is down:

Fluent Bit stores logs locally in: memory OR disk

No logs lost. Containers never fail.

#### Step 5: Local agent forwards logs to central machine

Logs sent over network.

#### Step 6: Central Log Collector receives logs

It aggregates logs from all machines.

Example:
```
[0] service-a: [[1771480560.000000000, {}], {"source"=>"stdout", "log"=>"2026-02-19 05:56:00,189 | INFO | service-a | Processing request number 19", "container_id"=>"c2c058758236ea2b081ecde07e91baeb0297cdd8678bd61efebd92ea2edbdf51", "container_name"=>"/service-a"}]
```
### Process -2 Without using a Local Logging Agent

Now with this process there was a slight problem that when we will send the logs directly to the central machine from each machine using a logging driver then if the central machine or the container is down then the logs might get lost. So to avoid this we can save the logs in a local file in each machine where the micro-services are running. For example in python we can use **basicConfig()** module or **Winston/Pino**(in Node.js/ts) to specify the file where the logs will be solved.

Example:
```python
import logging
logging.basicConfig(
    filename='app.log',
    filemode='a',  # 'a' appends to file (default), 'w' overwrites each time
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info('This message will be written to the file.')
logging.warning('This is a warning.')
logging.error('This is an error.')

```

But if the logs are saved in a folder then docker will not be able to get the logs from the file as it can only read from stdout/stderr. So for that we need to write our code in a way by which logs will be saved in a local file and the logs will go to stdout as well.
```python
import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | service-a | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),      
        logging.FileHandler("service-a.log")    
    ]
)

logger = logging.getLogger("service-a")

def run():
    counter = 0
    while True:
        logger.info(f"Processing request number {counter}")
        counter += 1
        time.sleep(3)

if __name__ == "__main__":
    run()
```

### Architecture
```
            MACHINE 1                                                 MACHINE 2
┌───────────────────────────────┐                        ┌───────────────────────────────┐
│ Python Microservice Container │                        │ Node.js Microservice Container│
│                               │                        │                               │
└───────────────┬───────────────┘                        └───────────────┬───────────────┘
                │                                                        │
                ▼                                                        ▼
      ┌─────────────────────┐                                 ┌─────────────────────┐
      │  Python Logging     │                                 │  Winston / Pino     │
      │       Module        │                                 │  Logging Library    │
      └──────────┬──────────┘                                 └──────────┬──────────┘
                 │                                                       │
                 ▼                                                       ▼
      ┌─────────────────────┐                                 ┌─────────────────────┐
      │  Save logs locally  │                                 │  Save logs locally  │
      │  /var/log/app.log   │                                 │  /var/log/app.log   │
      │  (backup/prevent    │                                 │  (backup/prevent    │
      │   loss)             │                                 │   loss)             │
      └──────────┬──────────┘                                 └──────────┬──────────┘
                 │                                                       │
                 ▼                                                       ▼
      ┌─────────────────────┐                                 ┌─────────────────────┐
      │  STDOUT / STDERR    │                                 │  STDOUT / STDERR    │
      │  (console output)   │                                 │  (console output)   │
      └──────────┬──────────┘                                 └──────────┬──────────┘
                 │                                                       │
                 ▼                                                       ▼
      ┌─────────────────────┐                                 ┌────────────────────┐
      │  Docker Logging     │                                 │  Docker Logging    │
      │       Driver        │                                 │       Driver       │
      └──────────┬──────────┘                                 └─────────┬──────────┘
                 │                                                      │
                 └───────────────────── TCP 514 ────────────────────────┘
                                            │
                                            ▼
                         ┌────────────────────────────────────────┐
                         │           CENTRAL MACHINE              │
                         │                                        │
                         │       Fluent Bit / rsyslog             │
                         │                                        │
                         │     Receive logs from both machines    │
                         │                │                       │
                         │                ▼                       │
                         │       Parse / Filter logs              │
                         │                │                       │
                         │                ▼                       │
                         │       Store logs centrally             │
                         │      /var/log/central/*.log            │
                         │      or Elasticsearch / DB             │
                         │                │                       │
                         │                ▼                       │
                         │       Forward logs to remote           │
                         └────────────────┬───────────────────────┘
                                          │
                                          │  TCP / HTTPS / Syslog
                                          │
                                          ▼
                         ┌────────────────────────────────────────┐
                         │         REMOTE SERVER/MACHINE          │ 
                         │                                        │
                         │         Log Storage & Analysis         │
                         │  (Grafana Loki / Elasticsearch / S3)   │
                         └────────────────────────────────────────┘
```
Now with this process a slight problem occures that when we will send the logs directly to the central machine from each machine using a logging driver then if the central machine or the container is down then the logs might get lost 
**Step-by-Step Flow Explanation**

#### Step - 1: Microservices generates logs
Different micro-services generate logs.
#### Step - 2: Logs are written to TWO places

##### A. Local file (backup)
```
/var/log/app.log
```
Purpose:

. Prevent log loss

. Local debugging

. Recovery if network fails

##### B. STDOUT / STDERR

Container output stream: stdout, stderr . Docker captures this.

#### Step - 3: Docker logging driver captures logs
Docker daemon reads container stdout/stderr.
#### Step - 4: Docker sends logs to central machine
Docker sends logs to the central machine using a tcp/udp protocol
#### Step - 5: Central machine/container receives logs from different source
Central machine uses a log collector(e.g., fluent bit, rsyslog) to collect logs coming from different micro-services.
#### Step - 6: Log processing and storing
It receive logs, parse them, add metadata, filter them and forward the logs to a remote machine.
#### Step -7: Log forwarding to a remote machine
Logs can be forwarded to a remote machine, Grafana, Loki or S3 etc. .
