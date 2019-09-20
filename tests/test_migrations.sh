#!/usr/bin/env bash
#

# Fail if any command fails
# http://stackoverflow.com/questions/90418/exit-shell-script-based-on-process-exit-code
set -e
set -o pipefail

if [ "$TRAVIS" == "true" ]
then
  # If not on Travis, then create databases
  echo "Creating Postgres database and user"
  psql -c "DROP ROLE IF EXISTS travis"
  psql -c "CREATE ROLE travis LOGIN PASSWORD ''"
  psql -c "DROP DATABASE IF EXISTS oscar_travis"
  psql -c "CREATE DATABASE oscar_travis"
fi

# Postgres
echo "Running migrations against Postgres"
./manage.py migrate --noinput
