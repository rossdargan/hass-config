#!/bin/bash
FileYouWantToTest='/docker/global/travis/scripts/update-hass.txt'
echo -n "Verifying if $FileYouWantToTest exist..."
if [ -f $FileYouWantToTest ]
    then
        rm -f $FileYouWantToTest
        ./pull.sh
	
	cd /docker/homeassistant
	echo -n "Pulling from Git"
	git pull origin master
 	echo -n "Restarting docker"
	docker restart home-assistant
fi
exit 0
