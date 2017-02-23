#!/bin/bash

if [ $# -lt 2 ]
then
    echo "use: $0 <host> <config file> [<sleep time>]"
else
    #export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./gmone.jar
    export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./bin
    if [ $# -eq 3 ]
    then
    	echo "Sleeping $3 seconds before starting the monitor..."
    	sleep $3
    fi
    java -Djava.net.preferIPv4Stack=true gmonemon.GMonEMonService $1 $2
fi
