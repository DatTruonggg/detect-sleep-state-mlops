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
            agent {
                docker {
                    image 'python:3.10-slim' 
                }
            }
            steps {
                script {
                    echo 'Running tests...'
                    sh 'python --version'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building Docker image...'

                    if (!fileExists('docker/dockerfile.app')) {
                        error "Dockerfile not found. Build failed!"
                    }

                    dockerImage = docker.build("${registry}:latest", "--file docker/dockerfile.app .")

                    echo 'Pushing image to Docker Hub...'
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
                    echo 'Deploying application locally...'
                }
            }
        }
    }
}
