
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        string(
            name: 'IMAGE_TAG',
            defaultValue: '1.0',
            description: 'Docker image version'
        )

        string(
            name: 'TARGET_HOST',
            defaultValue: '',
            description: 'Application EC2 Public IP'
        )
    }

    environment {
        AWS_REGION = 'ap-southeast-2'
        AWS_ACCOUNT_ID = '266294230860'

        ECR_REGISTRY = '266294230860.dkr.ecr.ap-southeast-2.amazonaws.com'

        DEPLOY_USER = 'ubuntu'
        DEPLOY_DIR = '/home/ubuntu/cicd-project/aws-microservices-cicd'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checkout completed.'
            }
        }

        stage('Configuration Validation') {
            steps {
                sh '''
                    set -e

                    test -f compose.yaml
                    test -f user-service/Dockerfile
                    test -f product-servic/Dockerfile
                    test -f order-service/Dockerfile

                    docker compose -f compose.yaml config -q

                    echo "All configuration files validated."
                '''
            }
        }

        stage('Application Testing') {
            steps {
                sh '''
                    set -e

                    test -f user-service/app.py
                    test -f product-servic/app.py
                    test -f order-service/app.py

                    echo "Application files verified."
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    set -e

                    docker build \
                      -t user-service:${IMAGE_TAG} \
                      ./user-service

                    docker build \
                      -t product-service:${IMAGE_TAG} \
                      ./product-servic

                    docker build \
                      -t order-service:${IMAGE_TAG} \
                      ./order-service

                    echo "All Docker images built successfully."
                '''
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    set -e

                    aws ecr get-login-password \
                      --region ${AWS_REGION} |
                    docker login \
                      --username AWS \
                      --password-stdin ${ECR_REGISTRY}

                    echo "ECR login successful."
                '''
            }
        }

        stage('Tag Images') {
            steps {
                sh '''
                    set -e

                    docker tag user-service:${IMAGE_TAG} \
                    ${ECR_REGISTRY}/user-service:${IMAGE_TAG}

                    docker tag product-service:${IMAGE_TAG} \
                    ${ECR_REGISTRY}/product-service:${IMAGE_TAG}

                    docker tag order-service:${IMAGE_TAG} \
                    ${ECR_REGISTRY}/order-service:${IMAGE_TAG}

                    echo "Images tagged successfully."
                '''
            }
        }

        stage('Push Images to ECR') {
            steps {
                sh '''
                    set -e

                    docker push ${ECR_REGISTRY}/user-service:${IMAGE_TAG}

                    docker push ${ECR_REGISTRY}/product-service:${IMAGE_TAG}

                    docker push ${ECR_REGISTRY}/order-service:${IMAGE_TAG}

                    echo "All images pushed to ECR."
                '''
            }
        }

        stage('Prepare Deployment Compose') {
            steps {
                script {
                    def deployCompose = """
services:
  user-service:
    image: ${env.ECR_REGISTRY}/user-service:${params.IMAGE_TAG}
    container_name: user-service
    ports:
      - "8081:5000"
    restart: unless-stopped

  product-service:
    image: ${env.ECR_REGISTRY}/product-service:${params.IMAGE_TAG}
    container_name: product-service
    ports:
      - "8082:5000"
    restart: unless-stopped

  order-service:
    image: ${env.ECR_REGISTRY}/order-service:${params.IMAGE_TAG}
    container_name: order-service
    ports:
      - "8083:5000"
    restart: unless-stopped
"""
                    writeFile(
                        file: 'deploy-compose.yaml',
                        text: deployCompose
                    )
                }
            }
        }

        stage('Deploy to Application EC2') {
            steps {
                script {
                    if (!params.TARGET_HOST?.trim()) {
                        error('Please provide Application EC2 Public IP in TARGET_HOST.')
                    }

                    sshagent(credentials: ['ec2-deploy-key']) {
                        sh '''
                            set -e

                            ssh -o StrictHostKeyChecking=no \
                              ${DEPLOY_USER}@${TARGET_HOST} \
                              "mkdir -p ${DEPLOY_DIR}"

                            scp -o StrictHostKeyChecking=no \
                              deploy-compose.yaml \
                              ${DEPLOY_USER}@${TARGET_HOST}:${DEPLOY_DIR}/compose.yaml

                            ssh -o StrictHostKeyChecking=no \
                              ${DEPLOY_USER}@${TARGET_HOST} \
                              "aws ecr get-login-password --region ${AWS_REGION} | sudo docker login --username AWS --password-stdin ${ECR_REGISTRY} && cd ${DEPLOY_DIR} && sudo docker compose pull && sudo docker compose up -d --remove-orphans"

                            echo "Deployment completed."
                        '''
                    }
                }
            }
        }

        stage('Deployment Verification') {
            steps {
                sshagent(credentials: ['ec2-deploy-key']) {
                    sh '''
                        set -e

                        ssh -o StrictHostKeyChecking=no \
                          ${DEPLOY_USER}@${TARGET_HOST} \
                          "cd ${DEPLOY_DIR} && sudo docker compose ps"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All microservices deployed successfully.'
        }

        failure {
            echo 'FAILURE: Pipeline failed. Check the Jenkins console output.'
        }

        always {
            echo 'CI/CD Pipeline execution completed.'
        }
    }
}
