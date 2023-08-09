#!/bin/bash

CONTAINER_ID=`docker ps --filter "name=gcc-container" --format '{{.ID}}'`

if ! [ -z "$CONTAINER_ID" ]; then
    docker stop "$CONTAINER_ID"
    docker remove "$CONTAINER_ID"
fi
