FROM ghcr.io/battleofthebots/botb-base-image:latest
RUN echo "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu focal main\ndeb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu focal main" >> /etc/apt/sources.list && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776 && apt update && apt install python3.7-distutils python3.7 -y
WORKDIR /opt
COPY requirements.txt requirements.txt
RUN python3.7 -m pip install -r requirements.txt
COPY static/ ./static
COPY templates/ ./templates
COPY system_gateway gateway_admin ./
RUN chown -R user:user /opt
USER user
CMD python3.7 gateway_admin && python3.7 system_gateway
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD [ $(curl -I -s http://0.0.0.0:80 | head -n 1 | cut -d' ' -f2 | head -n 1) -eq 200 ] || exit 1