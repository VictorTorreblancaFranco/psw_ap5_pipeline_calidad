FROM jenkins/jenkins:lts-jdk21

USER root

ARG JMETER_VERSION=5.6.3

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git maven python3 wget \
    && wget -q "https://downloads.apache.org/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz" \
         -O /tmp/apache-jmeter.tgz \
    && tar -xzf /tmp/apache-jmeter.tgz -C /opt \
    && ln -s "/opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter" /usr/local/bin/jmeter \
    && rm /tmp/apache-jmeter.tgz \
    && rm -rf /var/lib/apt/lists/*

ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:${PATH}

USER jenkins

RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    sonar \
    slack \
    junit \
    pipeline-stage-view \
    credentials-binding \
    htmlpublisher
