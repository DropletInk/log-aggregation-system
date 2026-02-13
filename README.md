# Aggregate logs from different microservices running in different containers in different machines into a central machine's container where we can manage the logs and send the logs somewhere else(another machine, LOKI etc.)
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

Pros: 

. Default (no config needed) 

. Works everywhere 

. Supports log rotation (log rotation: when a log file hits a size or time limit, it is renamed, often compressed, and a new file is created to continue logging). 

. Compatible with all collectors 

Cons:

. Stored in local storage, disk usage issue 

. No built-in forwarding 

. Host-dependent paths

### 2. journald (Host-centric) : 

Sends logs to systemd journal. systemd is the default system and service manager for most modern Linux distribution. It is a part of systemd. 

Collects logs from:  system services, kernel, Docker containers, stdout/stderr of processes, Stores logs in a binary journal, We don’t need to install it — it already exists on most Linux distros. 

Pros: 

. Centralized host logging 

. Built-in indexing and rotation 

. Metadata (unit, PID, container ID) 

Cons: 
. Requires systemd 

. Needs privileged access 

. Not portable across OS 

. Logs cannot be forwarded  

How journald works:  

1. Services write to stdout/stderr 

2.journald captures log message, service name, PID, UID, container name, timestamps 

3.Then logs are queried using: journalctl 

Example: journalctl CONTAINER_NAME=service-a -f 

``Log flow: Container -> journald -> journalctl`` 

### 3. syslog (Network Forwarding): 

Syslog is a standard protocol for message logging, allowing network devices, servers, and applications to generate, store, and analyze event logs centrally. 

. Sends logs to a syslog server 

. Uses TCP/UDP 

``Log flow: Container -> syslog -> log server`` 

Pros: 

. Simple & standardized 

. Remote shipping 

. Works with rsyslog / syslog-ng 

Cons: 

. UDP can drop logs 

. TCP can block containers 

. Docker blocks if syslog is slow 

 ## 4. fluentd (collector-friendly): 
 
 A log aggregation and forwarding platform, Written in Ruby, heavy, powerful, extremely flexible 

Acts as: collector, processor, router, shipper 

``Log flow: INPUT -> PARSER -> FILTER -> FILTER -> OUTPUT``

Pros: 
. Centralized logging: Aggregates logs from many nodes 

. Powerful processing: Parsing, Enrichment, Filtering, Conditional routing 

. Huge plugin ecosystem: 1000+ plugins, almost any input/output imaginable 

. Production-proven: Used at large scale (K8s, cloud providers) 

Cons:  

. Heavy, high memory & CPU usage 

. Operational complexity 

. Overkill for simple use cases 
## Aggregation Process
**What is Log Aggregation?** 

Log aggregation is the process of collecting logs from multiple services, machines, or containers and storing them in a single, centralized location for monitoring, debugging, and analysis. 

Now there are basically two ways to aggregate the logs in a central machine:
## Process - 1: Without a local logging agent
First we have to know how logging works. So basically in our system
