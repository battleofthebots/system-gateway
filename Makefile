# Make a zipfile that will be released for competitors
release:
	python3 -m compileall *.py
	mkdir build
	cp __pycache__/gateway_admin* build/gateway_admin.pyc
	cp __pycache__/system_gateway* build/__main__.pyc