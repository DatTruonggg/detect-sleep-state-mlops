DOCKER_IMAGE_NAME = dss-fastapi
DOCKER_TAG = latest
DOCKERFILE_PATH = docker/dockerfile.app
DOCKER_REGISTRY = dattruong1311
PORT = 8000

### ------ TEST -----
test-preprocess-stage: 
	bash src/test/test_feature_engineering.sh

### ------ DATA MERGING ------
merge: 
	poetry run python -m src.utils.transform.perform_merge_data --df_series data/raw/train_series.parquet --df_events data/raw/train_events.csv --output_dir data/processed/merge

down: 
	docker compose -f docker-compose-minio-local.yaml -f docker-compose-mlflow-local.yaml down

minio-local:
	$(MAKE) down
	docker compose -f docker-compose-minio-local.yaml up -d

mlflow-local:
	$(MAKE) down
	docker compose -f docker-compose-mlflow-local.yaml up -d

build-app:
	docker build -f docker/dockerfile.app -t dss-fastapi .

run-app: 
	docker run -p 8000:8000 dss-fastapi

tag:
	docker tag $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)

push-image: tag
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
app-docker:
	docker compose -f docker-compose-application.yaml up -d

jenkins:
	docker compose -f docker-compose-jenkins.yaml up -d