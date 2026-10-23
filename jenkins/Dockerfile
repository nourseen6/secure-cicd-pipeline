# Jenkins with the Docker CLI and the plugins this project needs.
FROM jenkins/jenkins:2.580.1-lts-jdk21

# Talk to the host's Docker engine through the mounted socket.
COPY --from=docker:29-cli /usr/local/bin/docker /usr/local/bin/docker

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Configure Jenkins from code (casc.yaml) instead of the setup wizard.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    CASC_JENKINS_CONFIG=/usr/share/jenkins/casc.yaml
COPY casc.yaml /usr/share/jenkins/casc.yaml
