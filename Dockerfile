FROM ubuntu:20.04

RUN apt update && \
    apt-get -y install python3 python3-pip build-essential nmap netcat curl wget vim iproute2 ftp iputils-ping && \
    pip install requests && \
    mkdir /flags/ && chmod 777 /flags

WORKDIR /opt
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY gateway_admin.py system_gateway.py ./
COPY static static
COPY templates templates
RUN python3 -m compileall *.py && cp __pycache__/system_gateway* __main__ && python3 gateway_admin.py

ENV SERIAL_NUMBER="10276-9245-18754"
CMD python3 __main__