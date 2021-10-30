#!/bin/bash
# This file contains script to pull the docker image from the docker-hub published for this application.
# After pulling the image it spins up the container on docker
# Once the spin up is successful, the application can be accessed at http://localhost:5000/.

docker pull abhigyani/location-simulator:v1.0.0
docker run -itd -p 5000:5000 abhigyani/location-simulator:v1.0.0

echo -e "\n\n*******************************\n"
echo -e "Application running at http://localhost:5000/ Please open in browser."
echo -e "\n\n*******************************\n"