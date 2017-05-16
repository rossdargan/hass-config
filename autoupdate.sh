#!/bin/bash
FileYouWantToTest='update.txt'
echo -n "Verifying if $FileYouWantToTest exist..."
if [ -f $FileYouWantToTest ]
    then
        rm -f $FileYouWantToTest
        ./pull.sh
fi
exit 0
