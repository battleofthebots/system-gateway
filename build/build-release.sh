docker build -t sg-build -f build/Dockerfile .
LATEST=$(docker run --rm -d -t sg-build sleep 120 | tee /dev/stderr)
docker cp $LATEST:/opt/system_gateway.zip system_gateway.zip
docker kill $LATEST
