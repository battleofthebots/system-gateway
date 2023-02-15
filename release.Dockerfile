FROM ubuntu:20.04

RUN apt update && \
    apt-get -y install python3 python3-pip build-essential nmap netcat curl wget vim iproute2 ftp iputils-ping && \
    pip install requests && \
    mkdir /flags/ && chmod 777 /flags

WORKDIR /opt
COPY . ./

RUN pip install -r requirements.txt

# Generate accounts for this instance
CMD bash entrypoint.sh