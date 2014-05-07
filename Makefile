# Shell to use with Make
SHELL := /bin/sh

# Set important paths
PROJECT := swarm
LOCALPATH := $(CURDIR)
PYTHON_BIN := $(VIRTUAL_ENV)/bin

# Testing Settins
TESTPATH := $(LOCALPATH)/tests
TEST_POSTFIX := --with-coverage --cover-package=$(PROJECT) --cover-inclusive --cover-erase

# Export targets not associated with files
.PHONY: test install showenv clean

# Show the virtual environment
showenv:
	@echo 'Environment:'
	@echo '------------------------'
	@$(PYTHON_BIN)/python -c "import sys; print 'sys.path:', sys.path"
	@echo 'PROJECT:' $(PROJECT)
	@echo 'TESTPATH:' $(TESTPATH)
	@echo 'VIRTUAL_ENV:' $(VIRTUAL_ENV)

# The test command to test our package
test:
	nosetests -v $(TEST_POSTFIX) $(TESTPATH)

# Install the package with the setup.py script
install:
	python setup.py install

# Clean build files
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
