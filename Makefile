V = 0
Q = $(if $(filter 1,$V),,@)

ifeq ($(OS),Windows_NT)
  VENV_PATH_DIR = Scripts
else
  VENV_PATH_DIR = bin
endif


historian-run:
	$(Q) docker compose -f docker/docker-compose.yaml up --build ngn_follower

historian-run-detached:
	$(Q) docker compose -f docker/docker-compose.yaml up --build -d ngn_follower

historian-logs:
	$(Q) docker compose -f docker/docker-compose.yaml logs -f

historian-down:
	$(Q) docker compose -f docker/docker-compose.yaml down
