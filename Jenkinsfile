pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }

    environment {
        registry = 'dattruong1311/dss-fastapi'
        registryCredential = 'dockerhub'
    }

    stages {
        stage('Test') {
            steps {
                script {
                    docker.image('python:3.10-slim').inside {
                        echo 'Testing model correctness..'
                        sh 'python --version'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building image for deployment..'
                    dockerImage = docker.build("${registry}:${BUILD_NUMBER}")

                    echo 'Pushing image to Docker Hub..'
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying application...'
                    sh '''
                    docker stop dss-fastapi || true
                    docker rm dss-fastapi || true
                    docker run -d --name dss-fastapi -p 8000:8000 ${registry}:latest
                    '''
                }
            }
        }
    }
}
