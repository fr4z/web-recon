#!/bin/bash	
docker build -t web-recon .
docker run -it -v $(pwd):/usr/src/app web-recon python3 recon.py $1