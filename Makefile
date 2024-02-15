.ONESHELL:

.DEFAULT_GOAL := venv

PYTHON = /bin/python3
PIP = /bin/pip
VENV = venv
PYTHON_VENV = ./$(VENV)/bin/python3
PIP_VENV = ./$(VENV)/bin/pip

venv/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	chmod +x ./$(VENV)/bin/activate
	source ./$(VENV)/bin/activate
	$(PIP_VENV) install -r requirements.txt

build: venv
	./build_files/utils/make_build_archive.py $(VERSION)

update_license: venv
	./tools/update_license.py $(LICENSE)

venv: venv/bin/activate

clean: venv
	pyclean .
	# rm -rf $(VENV)

.PHONY: build clean
