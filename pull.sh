#!/bin/bash

cd /docker/homeassistant/
git pull origin master
docker restart home-assistant
