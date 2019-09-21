#!groovy
// Check ub1 properties
properties([disableConcurrentBuilds()])

pipeline {
    agent {
        label 'master'
    }
    environment {
        COMPOSE_FILE = "test.yml"
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
    }
    stages {
        stage("Test") {
            steps {
                sh 'make test'
            }
        }
        stage("Deploy") {
            steps {
                sh "git push igor@panda_production:~/projects/panda HEAD:master"
            }
        }
        stage("Prepare") {
            steps {
                sh "ssh igor@panda_production '~/projects/panda/prepare.sh'"
            }
        }
        stage("Reload services") {
            steps {
                sh "ssh igor@panda_production 'sudo supervisorctl stop panda: && kill -9 `ps aux | grep /home/igor/.virtualenvs/panda/bin/gunicorn | awk '{ print $2 }'` && sudo supervisorctl start panda:'"
            }
        }
    }
}
