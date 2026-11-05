pipeline {
    agent any

    environment {
        IMAGE_TAG = '1.0'
    }

    stages {

        stage('Source Code Checkout') {
            steps {
                checkout scm
                echo 'Source code checkout successful'
            }
        }

        stage('Configuration Validation') {
            steps {
                sh '''
                    test -f compose.yaml
                    docker compose -f compose.yaml config -q
                    echo "Configuration validation successful"
                '''
            }
        }

        stage('Application Testing') {
            steps {
                sh '''
                    echo "Checking microservices"

                    for service in user-service product-servic order-service; do
                        if [ -d "$service" ]; then
                            echo "$service exists"
                        else
                            echo "$service directory missing"
                            exit 1
                        fi
                    done
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                echo 'Docker build will be configured after verifying Dockerfiles'
            }
        }

        stage('Image Tagging') {
            steps {
                echo 'Image tagging stage'
            }
        }

        stage('Amazon ECR Push') {
            steps {
                echo 'ECR push stage'
            }
        }

        stage('EC2 Deployment') {
            steps {
                echo 'EC2 deployment stage'
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully'
        }

        failure {
            echo 'Pipeline failed. Check Console Output.'
        }

        always {
            echo 'Pipeline execution finished'
        }
    }
}
