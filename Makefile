
# Управление сервисами
service-build:
	cd docker && docker-compose -f docker-compose.full.yml build

service-up:
	cd docker && docker-compose -f docker-compose.full.yml up -d

service-down:
	cd docker && docker-compose -f docker-compose.full.yml down

service-logs:
	cd docker && docker-compose -f docker-compose.full.yml logs -f

service-restart: service-down service-up

service-status:
	cd docker && docker-compose -f docker-compose.full.yml ps

# Тестирование API
test-api:
	bash scripts/test_api.sh

# Запуск воркера в фоне
run-worker:
	python -m src.main --mode worker

# Запуск API локально
run-api:
	python -m src.main --mode api

# Полный локальный запуск
run-local:
	bash scripts/run_local.sh
