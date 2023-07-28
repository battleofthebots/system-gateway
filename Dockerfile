FROM ghcr.io/battleofthebots/botb-base-image:latest
RUN add-apt-repository ppa:deadsnakes/ppa && apt update && apt install python3.7 -y

WORKDIR /opt
COPY static/ ./static
COPY templates/ ./templates
COPY system_gateway gateway_admin ./
CMD python3.7 gateway_admin && python3 system_gateway
