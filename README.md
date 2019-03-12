# anytime-tournament-bot

A Discord bot to enable mod-less anytime tournaments

# How to run
## Build docker image
docker build -t anytimebot .

## Run docker container using current sources
docker run -it --rm --volume $(pwd):/app anytimebot
