include .env

up:
	docker-compose --env-file .env up -d

down:
	docker-compose --env-file .env down	

ps:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

to_redpanda_console:
	open http://localhost:8080/topics