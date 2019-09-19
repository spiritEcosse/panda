#!/usr/bin/env bash

if [[ `git rev-parse --abbrev-ref HEAD` == 'master' ]]; then
	echo "begin deploy, show details in you ci"
	curl -X POST http://127.0.0.1:8094/job/panda/build?token=hRvyQqWEkbPUQrWwskihxmcBWirNFhnwdUITxhpJQbRjuUIKYPILhYQuVRegKzzN --user "igor:1111" -H "`wget -q --auth-no-challenge --user igor --password 1111 --output-document - 'http://127.0.0.1:8094/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)'`"
fi;
