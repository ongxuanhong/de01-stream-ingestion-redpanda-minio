include .env

build:
	docker-compose build

up:
	docker-compose --env-file .env up -d

down:
	docker-compose --env-file .env down	

ps:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

to_redpanda:
	open http://localhost:8080/topics

to_minio:
	open http://localhost:9001/buckets

to_mysql:
	docker exec -it mysql mysql -u"root" -p"${MYSQL_ROOT_PASSWORD}" ${MYSQL_DATABASE}	