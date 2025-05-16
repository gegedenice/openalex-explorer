#!/bin/bash

docker build -t openalex-explorer:latest .
docker run -d --name openalex-explorer -p 5000:5000 -v $(pwd)/files:/app/files openalex-explorer:latest