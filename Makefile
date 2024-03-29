.PHONY: sdk docker

.DEFAULT_GOAL := docker

test:
	python -m pytest -k

release:
	cd python-sdk &&\
	python ./setup.py clean &&\
	python ./setup.py sdist &&\
	python ./setup.py bdist_wheel &&\
	twine upload dist/*

docker:
	docker build . -t weopsproxy

