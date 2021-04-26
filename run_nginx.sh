#!/bin/bash

export PORT=${1:-3001}
export IPADDR=${IPADDR:-127.0.0.1}
echo "Starting volume 1 in port 3001..."
docker run --name nginx-$PORT -p $IPADDR:$PORT:3001 \
	-v $PWD/data:/usr/share/nginx/html \
	-v /home/nuxion/Proto/storepy/nginx-3001.conf:/etc/nginx/nginx.conf:ro \
       	-d nginx
