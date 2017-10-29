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
      environment {
        GRAPHDB_URI = credentials('GRAPHDB_URI')
        GRAPHDB_USER = credentials('GRAPHDB_USER')
        GRAPHDB_PASS = credentials('GRAPHDB_PASS')
      }
      steps {
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
