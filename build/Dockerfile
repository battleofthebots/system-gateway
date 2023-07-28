FROM python:3.7 as builder
RUN apt update && apt install -y zip
WORKDIR /opt
COPY src/ ./src
COPY static/ ./static
COPY templates/ ./templates
COPY requirements.txt ./
COPY Dockerfile ./
RUN python3.7 -m compileall src/*.py
RUN cp src/__pycache__/gateway_admin* gateway_admin
RUN cp src/__pycache__/system_gateway* system_gateway
RUN zip -r system_gateway.zip static templates requirements.txt system_gateway gateway_admin Dockerfile
#system_gateway.zip ends up in /opt/system_gateway.zip