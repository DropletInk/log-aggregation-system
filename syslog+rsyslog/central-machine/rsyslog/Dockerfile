FROM ubuntu:22.04
RUN apt-get update && apt-get install -y rsyslog iproute2 net-tools
COPY rsyslog.conf /etc/rsyslog.conf
CMD ["rsyslogd", "-n"]
