pipeline {
  agent any
  stages {
    stage('Run SonarQube') {
      steps {
        withSonarQubeEnv('speculum') {
          sh '/opt/sonar-scanner/bin/sonar-scanner'
        }

      }
    }

  }
}