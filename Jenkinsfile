pipeline {
  agent any
  
  environment {
    VENV = "/var/jenkins_home/virtualenvs/flask-neo4jdriver.${env.BUILD_NUMBER}"
    activate = ". ${env.VENV}/bin/activate"
  }

  stages {

    stage('Checkout') {
      steps {
        deleteDir()
            checkout scm
      }
    }

    stage('Build Notification') {
      steps {
        slackSend color: 'good', message: "Building Flask-Neo4jDriver [${env.BRANCH_NAME} - ${env.BUILD_NUMBER}]"
      }
    }

    stage('Create Virtual Environment') {
      steps {
        sh """#!/bin/bash
            set +x
            ${env.PYTHON} -m venv "${env.VENV}"
        """
      }
    }

    stage('Start Neo4j test instance') {
      steps {
        sh """#!/bin/bash
            docker pull neo4j:latest
            docker run -d --name "neo4j.${BUILD_NUMBER}" -p 127.0.0.1:7474:7474 -p 127.0.0.1:7687:7687 neo4j:latest
            sleep 15
            curl -v POST http://neo4j:neo4j@localhost:7474/user/neo4j/password -d"password=neo4j2"
            curl -v POST http://neo4j:neo4j2@localhost:7474/user/neo4j/password -d"password=neo4j"
        """
      }
    }

    stage('Run Tests') {
      steps {
        sh """#!/bin/bash
            ${env.activate}
            python setup.py test
        """
        step([$class: 'CoberturaPublisher', coberturaReportFile: 'results/coverage.xml', onlyStable: false])
      }
    }

    stage('Cleanup neo4j') {
      steps {
        sh """#!/bin/bash
            docker rm -f "neo4j.${BUILD_NUMBER}"
      }
    }
  }
  post {
    always {
      junit "results/junit.xml"
      sh """
          rm -rf "${env.VENV}"
      """
    }
    failure {
      slackSend color: 'bad', message: 'Build failed'
    }
    success {
      slackSend color: 'good', message: 'Build successful'
    }
  }
}
