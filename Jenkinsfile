pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'SIMULAR_FALLO',
            defaultValue: false,
            description: 'Genera un fallo controlado al final para evidenciar la alerta de Slack.'
        )
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 25, unit: 'MINUTES')
        skipDefaultCheckout(true)
    }

    environment {
        APP_PORT = '8085'
        SONAR_PROJECT_KEY = 'victor-torreblanca-psw-ap5'
        JMETER_PLAN = 'performance/pipeline-load-test.jmx'
        JMETER_RESULTS = 'target/jmeter/results.jtl'
        JMETER_REPORT = 'target/jmeter/report'
        SLACK_CHANNEL = '#jenkins-calidad-victor'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'mvn -B -ntp clean verify'
            }
            post {
                always {
                    junit allowEmptyResults: false,
                          testResults: 'target/surefire-reports/*.xml'
                    archiveArtifacts artifacts: 'target/*.jar,target/site/jacoco/**/*',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Análisis con SonarQube') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        mvn -B -ntp sonar:sonar \
                          -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                          -Dsonar.projectName="PSW AP5 - Pipeline de Calidad"
                    '''
                }
            }
        }

        stage('Pruebas con JMeter') {
            steps {
                sh '''
                    mkdir -p target/jmeter
                    rm -rf "$JMETER_REPORT" "$JMETER_RESULTS"

                    JENKINS_NODE_COOKIE=dontKillMe \
                      nohup java -jar target/psw-pipeline-base-0.0.1-SNAPSHOT.jar \
                      > target/application.log 2>&1 &
                    echo $! > target/application.pid

                    ready=false
                    for attempt in $(seq 1 60); do
                      if curl --fail --silent "http://localhost:$APP_PORT/actuator/health" > /dev/null; then
                        ready=true
                        break
                      fi
                      sleep 1
                    done

                    if [ "$ready" != "true" ]; then
                      echo "La aplicación no inició dentro del tiempo esperado."
                      exit 1
                    fi

                    jmeter -n \
                      -t "$JMETER_PLAN" \
                      -Jhost=localhost \
                      -Jport="$APP_PORT" \
                      -Jusers=50 \
                      -JrampUp=10 \
                      -Jloops=5 \
                      -l "$JMETER_RESULTS" \
                      -e -o "$JMETER_REPORT"

                    python3 scripts/analyze-jmeter.py "$JMETER_RESULTS" \
                      --output target/jmeter/summary.json \
                      --max-error-rate 1.0 \
                      --max-p95 2000
                '''
            }
            post {
                always {
                    sh '''
                        if [ -f target/application.pid ]; then
                          kill "$(cat target/application.pid)" 2>/dev/null || true
                        fi
                    '''
                    archiveArtifacts artifacts: 'target/jmeter/**/*,target/application.log',
                                     allowEmptyArchive: true
                    publishHTML target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'target/jmeter/report',
                        reportFiles: 'index.html',
                        reportName: 'Reporte JMeter'
                    ]
                }
            }
        }

        stage('Validación controlada') {
            steps {
                script {
                    if (params.SIMULAR_FALLO) {
                        error('Fallo controlado solicitado para demostrar la notificación FAILURE.')
                    }
                    echo 'Las etapas técnicas finalizaron correctamente.'
                }
            }
        }

        stage('Notificación') {
            steps {
                slackSend(
                    channel: env.SLACK_CHANNEL,
                    color: 'good',
                    message: """✅ PIPELINE EXITOSO
Proyecto: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
SonarQube y JMeter ejecutados correctamente.
Detalles: ${env.BUILD_URL}"""
                )
            }
        }
    }

    post {
        failure {
            slackSend(
                channel: env.SLACK_CHANNEL,
                color: 'danger',
                message: """❌ PIPELINE FALLIDO
Proyecto: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
Revisar: ${env.BUILD_URL}"""
            )
        }
        cleanup {
            sh '''
                if [ -f target/application.pid ]; then
                  kill "$(cat target/application.pid)" 2>/dev/null || true
                fi
            '''
        }
    }
}
