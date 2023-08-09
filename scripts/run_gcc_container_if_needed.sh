#!/bin/bash

GCC_PROCESS=`docker ps --filter "name=gcc-container" --format '{{.Names}}'`

if [ -z "$GCC_PROCESS" ]; then
	docker run -d -it --name gcc-container gcc-image
fi
