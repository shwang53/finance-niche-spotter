.DEFAULT_GOAL := reload

reload: down build up
	docker-compose up -d

up: 
	docker-compose up -d

down:
	docker-compose down

ps:
	docker-compose ps

build:
	docker-compose build
