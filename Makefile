# django
migrations:
	./manage.py makemigrations

showmigrations:
	./manage.py showmigrations

migrate:
	./manage.py migrate

run:
	./manage.py runserver

shell:
	./manage.py shell

# linting
format:
	ruff format .

check:
	ruff check .

fix:
	ruff check --fix .

lint:
	ruff check .
	ruff format .
	ruff check --fix .

# testing

test:
	python -m pytest -vvv
	coverage html
