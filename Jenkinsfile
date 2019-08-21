#!groovy
// Check ub1 properties
properties([disableConcurrentBuilds()])

pipeline {
    agent {
        label 'develop'
    }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        timestamps()
    }
    stages {
        stage("First step") {
            steps {
                sh 'ssh igor@panda_production \'hostname\''
            }
        }
        stage("Second step") {
            steps {
                sh 'ssh igor@panda_production \'uptime\''
            }
        }
    }
}

