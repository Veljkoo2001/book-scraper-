# Makefile
.PHONY: help build run test clean logs export

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker image"
	@echo "  make run      - Run scraper"
	@echo "  make test     - Run tests"
	@echo "  make shell    - Open shell in container"
	@echo "  make logs     - Show logs"
	@echo "  make clean    - Remove containers and images"
	@echo "  make export   - Export data from container"

build:
	docker-compose build

run:
	docker-compose up scraper

test:
	docker-compose run --rm scraper python -m pytest tests/ -v

shell:
	docker-compose run --rm scraper /bin/bash

logs:
	docker-compose logs -f scraper

clean:
	docker-compose down -v
	docker system prune -f

export:
	docker cp advanced_scraper:/app/data/exports ./exports/
	@echo "Data exported to ./exports/"