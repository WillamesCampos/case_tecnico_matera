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

# docker

up:
	cd infrastructure && docker compose up -d

upbuild:
	cd infrastructure && docker compose up --build -d

docker-logs:
	cd infrastructure && docker compose logs -f web

docker-down:
	cd infrastructure && docker compose down

docker-ps:
	cd infrastructure && docker compose ps
