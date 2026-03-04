# Log rotation configuration

## Step-1

Add this OUTPUT section in the ``fluent-bit.conf`` file. This allows the fluent-bit to create log files automatically for each containers based on the container name.

```bash
[OUTPUT]
    Name         file
    Match        *
    Path         /var/log/fluentbit
```
## Step-2

Create a ``log`` folder where our log files for each container will be created

## Step-3

Mount the volume with the log folder

```docker
services:
  fluent-bit:
    image: fluent/fluent-bit:2.2
    container_name: local-fluent-bit
    ports:
      - "24224:24224"
      - "24224:24224/udp"
    volumes:
      - ./fluent-bit/fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
      - ./logs:/var/log/fluentbit
    command: -c /fluent-bit/etc/fluent-bit.conf
    restart: always
```
## Step-4

Open the log rotaion config file 

```
sudo /etc/logrotate.d/fluentbit-services
```
## Step-5

Write the configuration for the log rotation

```
/home/ntpl/local-logging-agent/local-logging/logs/* {  # log file 
directory

#run log rotation as User-root and Group-root   
 su root root

#rotate logs once per day
    daily

#keep 7 rotated log files, then deletes older ones
    rotate 7

#compress rotated log files using gzip
    compress

#if the log file doesn't exist, do not throw an error
    missingok

#don't rotate the log file if it is empty
    notifempty

#copy the current log file to a rotated file, then truncate(empty) the original file
    copytruncate

#it adds a date extension to rotated files instead of numbers ex- service-a-2026-04-03
    dateext

#defines the format of the date
    dateformat -%Y-%m-%d
}

```

## Step-6
save the file

```bash
Press ctr+o
then hit Enter button
```

## Step-7
To test if the log rotation is working or not we don't need to wait for a day we can test it manually. But before that ensure the containers are running and log files are created. Then run this command:

```bash
sudo logrotate --force /etc/logrotate.d/fluentbit-services
```

``NOTE:`` This process will only work in linux based systems. 

