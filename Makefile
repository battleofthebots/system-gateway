# Make a zipfile that will be released for competitors
PREFIX_DIR := challenge
PYTHON_CMD := python3.8

release: clean
	$(PYTHON_CMD) -m compileall $(PREFIX_DIR)/*.py
	mkdir -p build
	cp $(PREFIX_DIR)/__pycache__/gateway_admin* build/gateway_admin
	cp $(PREFIX_DIR)/__pycache__/system_gateway* build/system_gateway
	cp release.Dockerfile build/Dockerfile
	cp -r $(PREFIX_DIR)/static $(PREFIX_DIR)/templates $(PREFIX_DIR)/requirements.txt $(PREFIX_DIR)/entrypoint.sh build/
	cd build && zip -r ../system_gateway_release.zip *

clean:
	rm -fr build/
	find . -type d -name __pycache__ -exec rm -rfv {} \; && echo -n