
pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_TAG', defaultValue: '1.0',
               description: 'Docker image version')

        string(name: 'TARGET_HOST', defaultValue: '',
               description: 'Application EC2 IP')
    }

    environment {
        AWS_REGION     = 'ap-southeast-2'
        AWS_ACCOUNT_ID = '266294230860'
        ECR_REGISTRY   = '266294230860.dkr.ecr.ap-southeast-2.amazonaws.com'

        DEPLOY_USER = 'ubuntu'
        DEPLOY_DIR  = '/home/ubuntu/cicd-project/aws-microservices-cicd'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
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
                    for service in user-service product-service order-service
                    do
                        test -d "$service"
                        echo "$service directory verified"
                    done
                '''
            }
        }

        stage('Docker Image Build') {
            steps {
                sh '''
                    set -e
                    docker build -t user-service:${IMAGE_TAG} ./user-service
                    docker build -t product-service:${IMAGE_TAG} ./product-service
                    docker build -t order-service:${IMAGE_TAG} ./order-service
                '''
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    set -e
                    aws ecr get-login-password --region ${AWS_REGION} |
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Tag Images') {
            steps {
                sh '''
                    set -e
                    docker tag user-service:${IMAGE_TAG} ${ECR_REGISTRY}/user-service:${IMAGE_TAG}
                    docker tag product-service:${IMAGE_TAG} ${ECR_REGISTRY}/product-service:${IMAGE_TAG}
                    docker tag order-service:${IMAGE_TAG} ${ECR_REGISTRY}/order-service:${IMAGE_TAG}
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

                        test -n "${TARGET_HOST}"

                        ssh -o BatchMode=yes ${DEPLOY_USER}@${TARGET_HOST} \
                            "mkdir -p ${DEPLOY_DIR}"

                        scp -o BatchMode=yes compose.yaml \
                            ${DEPLOY_USER}@${TARGET_HOST}:${DEPLOY_DIR}/compose.yaml

                        ssh -o BatchMode=yes ${DEPLOY_USER}@${TARGET_HOST} \
                            "ECR_REGISTRY='${ECR_REGISTRY}' \
                             IMAGE_TAG='${IMAGE_TAG}' \
                             AWS_REGION='${AWS_REGION}' \
                             DEPLOY_DIR='${DEPLOY_DIR}' bash -s" <<'REMOTE'

                        set -e
                        cd "$DEPLOY_DIR"

                        aws ecr get-login-password --region "$AWS_REGION" |
                        sudo docker login --username AWS --password-stdin "$ECR_REGISTRY"

                        sudo -E env ECR_REGISTRY="$ECR_REGISTRY" IMAGE_TAG="$IMAGE_TAG" \
                            docker compose pull

                        sudo -E env ECR_REGISTRY="$ECR_REGISTRY" IMAGE_TAG="$IMAGE_TAG" \
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
                        ssh -o BatchMode=yes ${DEPLOY_USER}@${TARGET_HOST} \
                            "cd ${DEPLOY_DIR} && sudo docker compose ps"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'All three microservices deployed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}
