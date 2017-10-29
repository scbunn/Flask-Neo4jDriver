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
      post {
        failure {
          script { env.FAILURE_STAGE = "Create Virtual Environment" }
        }
      }
    }

    stage('Run Tests') {
      steps {
        withCredentials([$class: 'StringBinding', credentialsId: 'GRAPHDB_URI', variable: 'GRAPHDB_URI'])
        withCredentials([$class: 'StringBinding', credentialsId: 'GRAPHDB_USER', variable: 'GRAPHDB_USER'])
        withCredentials([$class: 'StringBinding', credentialsId: 'GRAPHDB_PASS', variable: 'GRAPHDB_PASS'])
        sh """#!/bin/bash
            ${env.activate}
            python setup.py test
        """
        step([$class: 'CoberturaPublisher', coberturaReportFile: 'results/coverage.xml', onlyStable: false])
      }
      post {
        failure {
          script { env.FAILURE_STAGE = "Failed Tests" }
        }
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
      slackSend color: 'bad', message: "Build failed: ${env.FAILURE_STAGE}"
    }
    success {
      slackSend color: 'good', message: 'Build successful'
    }
  }
}
