
pipeline {
    agent any

    parameters {
        string(
            name: 'IMAGE_TAG',
            defaultValue: '1.0',
            description: 'Docker image version'
        )

        string(
            name: 'TARGET_HOST',
            defaultValue: '',
            description: 'Application EC2 public or private IP'
        )
    }

    environment {
        AWS_REGION     = 'ap-southeast-2'
        AWS_ACCOUNT_ID = 'YOUR_AWS_ACCOUNT_ID'
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

        DEPLOY_USER    = 'ubuntu'
        DEPLOY_DIR     = '/home/ubuntu/cicd-project/aws-microservices-cicd'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully'
            }
        }

        stage('Configuration Validation') {
            steps {
                sh '''
                    set -e

                    test -f compose.yaml
                    test -f user-service/Dockerfile
                    test -f product-service/Dockerfile
                    test -f order-service/Dockerfile

                    docker compose -f compose.yaml config -q

                    echo "Configuration validation successful"
                '''
            }
        }

        stage('Application Testing') {
            steps {
                sh '''
                    set -e

                    echo "Checking microservice directories"

                    for service in user-service product-service order-service
                    do
                        test -d "$service"
                        echo "$service exists"
                    done

                    echo "Basic application structure validation passed"
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
                      ./product-service

                    docker build \
                      -t order-service:${IMAGE_TAG} \
                      ./order-service
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
                '''
            }
        }

        stage('Tag Docker Images') {
            steps {
                sh '''
                    set -e

                    docker tag user-service:${IMAGE_TAG} \
                      ${ECR_REGISTRY}/user-service:${IMAGE_TAG}

                    docker tag product-service:${IMAGE_TAG} \
                      ${ECR_REGISTRY}/product-service:${IMAGE_TAG}

                    docker tag order-service:${IMAGE_TAG} \
                      ${ECR_REGISTRY}/order-service:${IMAGE_TAG}
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
                '''
            }
        }

        stage('Deploy to Application EC2') {
            steps {
                sshagent(credentials: ['ec2-deploy-key']) {
                    sh '''
                        set -e

                        if [ -z "${TARGET_HOST}" ]; then
                            echo "ERROR: TARGET_HOST parameter is required"
                            exit 1
                        fi

                        # Copy Compose configuration to application EC2
                        ssh -o BatchMode=yes \
                            ${DEPLOY_USER}@${TARGET_HOST} \
                            "mkdir -p ${DEPLOY_DIR}"

                        scp -o BatchMode=yes \
                            compose.yaml \
                            ${DEPLOY_USER}@${TARGET_HOST}:${DEPLOY_DIR}/compose.yaml

                        # Deploy using the EC2 instance IAM role
                        ssh -o BatchMode=yes \
                            ${DEPLOY_USER}@${TARGET_HOST} \
                            "ECR_REGISTRY='${ECR_REGISTRY}' \
                             IMAGE_TAG='${IMAGE_TAG}' \
                             AWS_REGION='${AWS_REGION}' \
                             DEPLOY_DIR='${DEPLOY_DIR}' bash -s" <<'REMOTE'

                        set -e

                        cd "$DEPLOY_DIR"

                        aws ecr get-login-password \
                          --region "$AWS_REGION" |
                        sudo docker login \
                          --username AWS \
                          --password-stdin "$ECR_REGISTRY"

                        sudo -E env \
                          ECR_REGISTRY="$ECR_REGISTRY" \
                          IMAGE_TAG="$IMAGE_TAG" \
                          docker compose pull

                        sudo -E env \
                          ECR_REGISTRY="$ECR_REGISTRY" \
                          IMAGE_TAG="$IMAGE_TAG" \
                          docker compose up -d --remove-orphans

                        sudo docker compose ps

                        REMOTE
                    '''
                }
            }
        }

        stage('Deployment Verification') {
            steps {
                sshagent(credentials: ['ec2-deploy-key']) {
                    sh '''
                        ssh -o BatchMode=yes \
                            ${DEPLOY_USER}@${TARGET_HOST} \
                            "cd ${DEPLOY_DIR} && sudo docker compose ps"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All three microservices deployed successfully!'
        }

        failure {
            echo 'FAILED: Pipeline failed. Check Console Output.'
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}
