.PHONY: typehint
typehint:
	mypy --ignore-missing-imports monolithcaching/

.PHONY: lint
lint:
	pylint monolithcaching/

.PHONY: black
black:
	black -1 79 monolithcaching/

.PHONY: clean
clean:
	find . -type f -name "*.pyc" | xargs rm -fr
	find . -type d -name __pycache__ | xargs rm -fr
