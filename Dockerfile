FROM golang:1.13-buster

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get -y install git nmap

# assetfinder
RUN go get -u github.com/tomnomnom/assetfinder

# httprobe
RUN go get -u github.com/tomnomnom/httprobe

# gobuster
RUN go get github.com/OJ/gobuster

# gowitness
RUN true \
    && go get -u github.com/sensepost/gowitness

RUN true \
	&& apt-get update \
	&& apt-get install -yyq ca-certificates \
	&& apt-get install -yyq libappindicator1 libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
	&& apt-get install -yyq gconf-service lsb-release wget xdg-utils \
	&& apt-get install -yyq fonts-liberation \
	&& apt-get install -yyq chromium
