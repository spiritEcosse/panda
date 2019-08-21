#!groovy
// Check ub1 properties
properties([disableConcurrentBuilds()])

pipeline {
    agent {
        label 'master'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
    }
    stages {
        stage("Check build by docker-compose") {
            steps {
                docker-compose -f production.yml up
            }
        }
        stage("Deploy to production") {
            steps {
                sh 'ssh igor@panda_production \'uptime\''
            }
        }
    }
}
