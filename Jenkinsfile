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
                sh 'ssh igor@panda_production \'uptime\''
            }
        }
    }
    post {
        always {
            sh "docker-compose down -v"
        }
    }
}
