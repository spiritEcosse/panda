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
                make deploy_production
            }
        }
        stage("Deploy to production") {
            steps {
                sh 'ssh igor@panda_production \'uptime\''
            }
        }
    }
}
