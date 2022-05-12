#!/bin/bash -xe

# Only run docker-compose down
if [[ $1 == "--down" ]]; then
  docker-compose -f docker/docker_compose.yml --env-file docker/default_config.env down "$2"
  exit 1
fi

docker build -t financial_news .
docker-compose -f docker/docker_compose.yml --env-file docker/default_config.env up -d
