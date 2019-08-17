#!/usr/bin/env bash

curl -L -O https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.4.6/elasticsearch-2.4.6.tar.gz
tar -xvf elasticsearch-2.4.6.tar.gz
cd elasticsearch-2.4.6/bin
./elasticsearch &
