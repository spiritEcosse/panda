FROM solr:8

ENV PYTHONUNBUFFERED 1

USER root

RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN apt-get install -y postgresql-client
#RUN apt-get install -y postgresql-dev
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install django==2.2.4
RUN pip install pysolr==3.8.1
RUN pip install ipython

USER solr
