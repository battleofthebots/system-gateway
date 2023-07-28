#!/bin/bash
docker build -t sg-build -f build/Dockerfile .
LATEST=$(docker run --rm -d -t sg-build sleep 120 | tee /dev/stderr)                                                                                      
docker cp $LATEST:/opt/system_gateway system_gateway                                                                                                    
docker cp $LATEST:/opt/gateway_admin gateway_admin                                                                                                      
docker kill $LATEST
