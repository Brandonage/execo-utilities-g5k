#!/bin/bash

if [ $# -ne 1 ]
then
    echo "use: $0 <database file>"
else
    export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./gmone.jar
    #export CLASSPATH=./:`echo lib/*.jar | sed s/" "/":"/g`:./bin
    if ! [ -e $1 ]
    then
        echo "$3 database file not found. Creating it..."
	java gmonedb.DBCreator $1
    fi
fi