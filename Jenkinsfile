pipeline {
  agent any
  stages {
    stage('Install build dependencies') {
      parallel {
        stage('Install build dependencies') {
          steps {
            sh 'pip install -U --upgrade pip pytest setuptools setuptools-git-version'
          }
        }

        stage('Run SonarQube') {
          steps {
            withSonarQubeEnv('speculum') {
              sh '/opt/sonar-scanner/bin/sonar-scanner'
            }

          }
        }

      }
    }

    stage('Run pytest') {
      steps {
        sh 'python3 -m pytest'
      }
    }

  }
}