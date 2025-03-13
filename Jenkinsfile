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
                    echo 'Running tests...'
                    sh 'python --version'  // Kiểm tra Python đã cài đúng chưa
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building Docker image...'

                    // Kiểm tra xem Dockerfile có tồn tại không
                    if (!fileExists('Dockerfile')) {
                        error "Dockerfile not found. Build failed!"
                    }

                    dockerImage = docker.build("${registry}:${BUILD_NUMBER}")

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
