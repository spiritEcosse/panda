#!/usr/bin/env bash

source `which virtualenvwrapper.sh` 		&&
workon panda                                &&
cd ~/projects/panda							&&
git reset --hard							&&
pip install -r requirements.txt             &&
python manage.py migrate                    &&
python manage.py rebuild_index  --noinput   &&
python manage.py collectstatic  --noinput

