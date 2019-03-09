
# You can set these variables from the command line.
LAMBDA_NAME  = avysms-entrypoint
BUNDLE_PATH  = ./avysms-entrypoint-lambda.zip
PYTHON       = ./venv/bin/python3
PIP          = ./venv/bin/pip3
LIVEREQUEST_URL = https://kq3r8wthij.execute-api.us-west-2.amazonaws.com/default/avysms-entrypoint
LIVEREQUEST_BODY = sangre

.PHONY: install freeze style test bundle deploy venv liverequest require_clean_git


install:
	pip3 install -r requirements-dev.txt
	python3 -m venv venv
	$(PIP) install -r requirements.txt


freeze:
	$(PIP) freeze > requirements.txt


style:
	pycodestyle


test: style
	$(PYTHON) -m unittest test/*.py


bundle: test
	rm $(BUNDLE_PATH) 2> /dev/null | true
	zip -r $(BUNDLE_PATH) ./*


deploy: require_clean_git bundle
	aws lambda update-function-code \
		--function-name "$(LAMBDA_NAME)" \
		--zip-file "fileb://$(BUNDLE_PATH)"


liverequest:
	curl --silent -X GET "$(LIVEREQUEST_URL)?Body=$(LIVEREQUEST_BODY)"


require_clean_git:
	git diff-index --quiet HEAD -- # Git repo is not clean
