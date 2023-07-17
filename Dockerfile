FROM ghcr.io/battleofthebots/botb-base-image:latest

WORKDIR /opt
#COPY challenge/requirements.txt .
#RUN pip install -r requirements.txt

COPY static/ ./static
COPY templates/ ./templates
COPY system_gateway gateway_admin ./
CMD python3 gateway_admin && python3 system_gateway
