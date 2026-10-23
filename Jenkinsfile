// The same pipeline as .github/workflows/ci.yml, on Jenkins.
// Each tool runs in its own container on the host's Docker engine, so
// Jenkins itself only needs the Docker CLI. See jenkins/ to run it locally.

pipeline {
    agent any

    parameters {
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false,
                     description: 'Push the scanned image to ghcr.io (needs a "ghcr" username/token credential)')
    }

    triggers {
        // A local Jenkins can't receive GitHub webhooks, so it checks for new commits every 5 minutes.
        pollSCM('H/5 * * * *')
    }

    options {
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        IMAGE        = "secure-cicd-pipeline:jenkins-${env.BUILD_NUMBER}"
        REGISTRY_IMG = 'ghcr.io/nourseen6/secure-cicd-pipeline'
    }

    stages {
        stage('Unit tests') {
            steps {
                // --volumes-from shares the Jenkins workspace with the test container.
                sh '''
                    docker run --rm --volumes-from jenkins -w "$WORKSPACE" \
                        -e PYTHONDONTWRITEBYTECODE=1 \
                        python:3.14-slim \
                        sh -c "pip install -q --root-user-action=ignore -r requirements-dev.txt && pytest -v -p no:cacheprovider"
                '''
            }
        }

        stage('Secret scan (gitleaks)') {
            steps {
                sh '''
                    docker run --rm --volumes-from jenkins \
                        -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
                        ghcr.io/gitleaks/gitleaks:v8.30.1 \
                        git "$WORKSPACE" --no-banner --redact
                '''
            }
        }

        stage('Build image') {
            steps {
                sh 'docker build -t "$IMAGE" .'
            }
        }

        stage('Image scan (Trivy)') {
            steps {
                sh '''
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/trivy \
                        aquasec/trivy:0.76.1 image \
                        --severity CRITICAL --ignore-unfixed --exit-code 1 --no-progress \
                        "$IMAGE"
                '''
            }
        }

        stage('Push image') {
            when { expression { params.PUSH_IMAGE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'ghcr',
                                                  usernameVariable: 'GHCR_USER',
                                                  passwordVariable: 'GHCR_TOKEN')]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
                        docker tag "$IMAGE" "$REGISTRY_IMG:jenkins-$BUILD_NUMBER"
                        docker push "$REGISTRY_IMG:jenkins-$BUILD_NUMBER"
                        docker logout ghcr.io
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rmi -f "$IMAGE" || true'
        }
    }
}
