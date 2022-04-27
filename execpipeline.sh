#!/bin/bash
while true; do eval "$(cat /docker/homeassistant/cmdpipe)" &> /docker/homeassistant/pipelog.txt; done
