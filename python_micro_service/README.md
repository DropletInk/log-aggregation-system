# python-microservices-for-logging
It includes 3 micro-services that has 3 levels of logs info, warn and error. Each service follows a standard log format:
```python
format='%(asctime)s | %(levelname)s | service-a | %(message)s'
```
We are using **logging.basicConfig()** module to define the log level and also used handler to decide the where the logs should go.

We have used two handlers:

**Streamhandler()** - It sends logs to stream, usually terminal(stdout) or error console(stderr)

**Filehandler()** - It sends logs to a file.

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | service-a | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),      
        logging.FileHandler("/logs/service-a.log")    
    ]
)
```
* **service-a** - It generates info level logs.
* **service-b** - It generates both info and warning level logs.
* **service-c** - It generates both info and error level logs.

## Folder Structure:
```
└── 📁python-micro-service-1
    └── 📁service-a
        ├── app.py
        ├── Dockerfile
    └── 📁service-b
        ├── app.py
        ├── Dockerfile
    └── 📁service-c
        ├── app.py
        ├── Dockerfile
    ├── docker-compose.yml
    └── README.md
```
## Dockerfile

The Dockerfile for each service is same.
```Docker
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

## docker-compose.yml
## Docker logging driver 

Here we have used **fluentd** as our docker logging driver.

## docker-compose.yml configuration for fluentd
```docker
    logging:
      driver: "fluentd" 
      options:
        fluentd-address: "tcp://192.168.49:2506" #ip address and the listening port of the central machine/server
        tag: "service-a" #tagging the service-name
```

**Pros:** 
* Centralized logging: Aggregates logs from many nodes

* Powerful processing: Parsing, Enrichment, Filtering, Conditional routing

* Huge plugin ecosystem: 1000+ plugins, almost any input/output imaginable

* Production-proven: Used at large scale (K8s, cloud providers)

**Cons:**

* Heavy, high memory & CPU usage

* Operational complexity

* Overkill for simple use cases

## Step by step commands to run

### Step-1: build the image
```docker
docker compose build
```
### Step-2: run the containers
```docker
docker compose up -d
```
### Step-3: check if the containers are running
```docker
docker ps
```
### Step-4: see the logs for a specific container
```docker
docker logs -f container_name 
```
After running the containers a logs file will be created where the logs of each file is being saved. We can see the logs from there also.
```
└── 📁python-micro-service-1
    └── 📁logs
        └── 📁service-a
            ├── service-a.log
        └── 📁service-b
            ├── service-b.log
        └── 📁service-c
            ├── service-c.log
```