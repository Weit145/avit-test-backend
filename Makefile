.PHONY: up seed

up:
	docker compose up --build -d

delete:
	docker compose down -v

down:
	docker compose down

test_unit:
	poetry run pytest -v

test_integration:
	docker compose --profile test up --build --abort-on-container-exit --exit-code-from integration-tests
	docker compose --profile test down -v

seed: up
	docker compose run --rm app python seed.py
в