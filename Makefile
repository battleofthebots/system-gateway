# Make a zipfile that will be released for competitors
PYTHON_CMD := python3.7

release: clean
	su -c 'add-apt-repository ppa:deadsnakes/ppa && apt update && apt install python3.7 -y'
	$(PYTHON_CMD) -m compileall src/*.py
	cp src/__pycache__/gateway_admin* gateway_admin
	cp src/__pycache__/system_gateway* system_gateway
	zip -r system_gateway.zip static templates requirements.txt system_gateway gateway_admin Dockerfile

clean:
	rm -fr build/
	find . -type d -name __pycache__ -exec rm -rfv {} \; && echo -n