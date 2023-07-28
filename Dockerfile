FROM ghcr.io/battleofthebots/botb-base-image:latest
RUN echo "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu focal main\ndeb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu focal main" >> /etc/apt/sources.list && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 && apt update && apt install python3.7-distutils python3.7 -y
WORKDIR /opt
COPY requirements.txt requirements.txt
RUN python3.7 -m pip install -r requirements.txt
COPY static/ ./static
COPY templates/ ./templates
COPY system_gateway gateway_admin ./
CMD python3.7 gateway_admin && python3.7 system_gateway
