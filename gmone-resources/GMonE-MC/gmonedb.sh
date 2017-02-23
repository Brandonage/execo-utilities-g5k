#!/bin/bash

if [ $# -ne 2 ]
then
    echo "use: $0 <host> <gmonedb config file>"
else
    #export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./gmone.jar
    export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./bin
    java -Djava.net.preferIPv4Stack=true gmonedb.GMonEDBService $1 $2
fi
