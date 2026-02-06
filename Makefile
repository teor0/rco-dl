.ONESHELL:
SHELL=/bin/bash

all:
	$(MAKE) help
help:
	@echo "--------------"
	@echo "		HELP     "
	@echo "--------------"
	@echo "make help"
	@echo "		Display help"
	@echo "make install"
	@echo "		Install everything"
	@echo "make clean"
	@echo "		Delete all the files"
	@echo "--------------"

install:
	@python3 -m venv .
	@source ./bin/activate
	@$(MAKE) requirements
	@$(MAKE) setup
	@echo "Install done"

setup:
	@cd ./bin
	@playwright install
	@cd ..
	@echo "setup done"

requirements:
	./bin/pip install -r requirements.txt

clean:
	@rm -rf __pycache__/
	@rm -rf bin/
	@rm -rf lib/
	@rm -rf lib64/
	@rm -rf include/
	@rm pyvenv.cfg
	@echo "Files deleted"

.PHONY: help install clean
