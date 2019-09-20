#!/usr/bin/env bash

if [[ `git rev-parse --abbrev-ref HEAD` == 'master' ]]; then
	echo "begin deploy, show details in you ci";
	java -jar jenkins-cli.jar -s http://127.0.0.1:8094/ build panda
fi;
