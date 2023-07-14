.PHONY: init install-dev-deps coverage reset fixtures fmt lfmt services \
	stop-services serve-django shell migrate

SHELL := /bin/bash

init: install-dev-deps services
	python manage.py collectstatic --no-input
	python manage.py test
	python manage.py migrate

install-dev-deps:
	poetry install --with dev

coverage:
	rm -rf htmlcov
	DJANGO_TEST=1 coverage run manage.py test
	coverage html
	firefox htmlcov/index.html

reset:
	python manage.py reset_db
	python manage.py migrate

fixtures:
	python manage.py init_site

fmt:
	@black --exclude __pycache__  config
	@black --exclude __pycache__ --exclude migrations simple_django
	@isort --skip migrations --skip __pycache__ simple_django
	@isort --skip __pycache__ config

lint:
	@flake8 config
	@flake8 simple_django

fmtl: fmt lint

services:
	docker-compose up -d

stop-services:
	docker-compose down

serve-django:
	python manage.py runserver_plus --keep-meta-shutdown

worker:
	celery -A config worker --loglevel=DEBUG

shell:
	python manage.py shell

migrate:
	python manage.py migrate
