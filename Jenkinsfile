pipeline {
    agent any
       
    environment {
        DOCKERHUB=credentials('dockerhub')
    }

    stages {
        stage('Build image') {
            steps {
                sh 'docker build -t fastapi-app .'
            }
        }
        
        stage('Push image to docker hub') {
            steps {            
                sh 'docker tag fastapi-app:latest renckel/fastapi-for-ci-cd:latest'
                sh 'echo $DOCKERHUB_PSW | docker login -u $DOCKERHUB_USR --password-stdin'
                
                sh 'docker push renckel/fastapi-for-ci-cd:latest'
            }
        }
        
        stage('Ansible pull image') {
            steps {
                ansiblePlaybook credentialsId: 'deploy-server', disableHostKeyChecking: true, installation: 'Ansible', inventory: '/etc/ansible/hosts', playbook: 'ansible-deploy.yml'
            }
        }
    }
}