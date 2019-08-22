#!groovy
// Check ub1 properties
properties([disableConcurrentBuilds()])

pipeline {
    agent {
        label 'master'
    }
    environment {
        COMPOSE_FILE = "production.yml"
        COMPOSE_PROJECT_NAME = "${env.JOB_NAME}-${env.BUILD_ID}"
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
    }
    stages {
        stage("Check build by docker-compose") {
            steps {
                sh 'make install'
            }
        }
        stage("Deploy to production") {
            steps {
                sh "ssh igor@panda_production"
#!/bin/bash
#source /webapps/hello_django/activate     # Activate the virtualenv
#cd /webapps/hello_django/trunk/
#pip install -r REQUIREMENTS.txt           # Install or upgrade dependencies
#python manage.py migrate                  # Apply South's database migrations
#python manage.py compilemessages          # Create translation files
#python manage.py collectstatic --noinput  # Collect static files
#supervisor panda                   # Restart the server, e.g. Apache
#python manage.py test --noinput app1 app2 # Run the tests
            }
        }
    }
    post {
        always {
            sh "docker-compose down -v"
        }
    }
}
