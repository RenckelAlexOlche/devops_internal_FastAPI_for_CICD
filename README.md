=================================DOCKERFILE=================================

```dockerfile
FROM python:3.10

ENV MYSQL_USER $MYSQL_USER
ENV MYSQL_PASSWORD $MYSQL_PASSWORD
ENV MYSQL_HOST $MYSQL_HOST
ENV MYSQL_PORT $MYSQL_PORT
ENV MYSQL_DB $MYSQL_DB
ENV JWT_SECRET $JWT_SECRET

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

#RUN alembic -c app/alembic.ini stamp head

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

This Dockerfile is used to create a Docker image for a Python application. Let's break down each line:

1. `FROM python:3.10`: 
   - This line specifies the base image to be used. In this case, it's the official Python image with version 3.10.

2. `ENV MYSQL_USER $MYSQL_USER` and the following `ENV` lines:
   - These lines set environment variables inside the Docker container. The values for these variables are taken from the build-time environment. They are related to MySQL database configuration and a JWT secret.

3. `WORKDIR /code`: 
   - This sets the working directory inside the container to `/code`. Any subsequent commands (like `COPY` or `RUN`) will be executed in this directory.

4. `COPY ./requirements.txt /code/requirements.txt`: 
   - This copies the `requirements.txt` file from the host machine (your computer) to the `/code` directory inside the container.

5. `RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt`: 
   - This installs the Python packages listed in `requirements.txt` using `pip`. The `--no-cache-dir` option ensures that the cache is not stored, which can help reduce the size of the image. The `--upgrade` option ensures that the latest versions of the packages are installed.

6. `COPY ./app /code/app`: 
   - This copies the `app` directory from the host machine to the `/code/app` directory inside the container.

7. `#RUN alembic -c app/alembic.ini stamp head`: 
   - This line is commented out (as indicated by the `#` at the beginning). If uncommented, it would run the `alembic` command with the specified configuration file to stamp the database schema version as "head". Alembic is a database migration tool for SQLAlchemy.

8. `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]`: 
   - This specifies the default command to run when the container starts. In this case, it's running the application using `uvicorn`, a lightweight ASGI server. The application is defined in the `main` module of the `app` package. The server will listen on all network interfaces (`0.0.0.0`) and port `80`.

In summary, this Dockerfile sets up a Python environment, installs the necessary packages, and prepares to run a Python application using Uvicorn when the container starts. The application seems to be related to a MySQL database, given the environment variables, and possibly uses Alembic for database migrations.

==================================JENKINS===================================

```groovy
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
```

This Jenkinsfile defines a continuous integration/continuous deployment (CI/CD) pipeline using Jenkins' declarative pipeline syntax. Let's break down each section:

1. `pipeline`: 
   - This keyword begins the definition of the pipeline.

2. `agent any`: 
   - This specifies that the pipeline can run on any available agent in the Jenkins environment.

3. `environment`: 
   - This section defines environment variables for the pipeline.
   - `DOCKERHUB=credentials('dockerhub')`: This retrieves the credentials named 'dockerhub' from Jenkins' credentials store and assigns them to the `DOCKERHUB` variable. These credentials are likely used for Docker Hub authentication.

4. `stages`: 
   - This begins the definition of the stages in the pipeline. Each stage represents a distinct phase of the CI/CD process.

5. `stage('Build image')`: 
   - This stage is responsible for building a Docker image.
   - `sh 'docker build -t fastapi-app .'`: This shell command builds a Docker image with the tag `fastapi-app` from the current directory (`.`).

6. `stage('Push image to docker hub')`: 
   - This stage pushes the built Docker image to Docker Hub.
   - `sh 'docker tag fastapi-app:latest renckel/fastapi-for-ci-cd:latest'`: This tags the `fastapi-app` image with a new tag, specifying the repository and tag on Docker Hub.
   - `sh 'echo $DOCKERHUB_PSW | docker login -u $DOCKERHUB_USR --password-stdin'`: This logs in to Docker Hub using the username and password from the `DOCKERHUB` credentials. The password is piped into `docker login` to avoid exposing it in the command line.
   - `sh 'docker push renckel/fastapi-for-ci-cd:latest'`: This pushes the tagged image to Docker Hub.

7. `stage('Ansible pull image')`: 
   - This stage uses Ansible to deploy the Docker image to a server.
   - `ansiblePlaybook ...`: This step runs an Ansible playbook.
     - `credentialsId: 'deploy-server'`: This specifies the credentials to use for the Ansible playbook, likely SSH credentials for the target server.
     - `disableHostKeyChecking: true`: This disables SSH host key checking, which can be useful in CI/CD environments where the target server's host key might not be known in advance.
     - `installation: 'Ansible'`: This specifies the Ansible installation to use.
     - `inventory: '/etc/ansible/hosts'`: This specifies the Ansible inventory file, which lists the target servers.
     - `playbook: 'ansible-deploy.yml'`: This specifies the Ansible playbook to run, which contains the instructions for deploying the Docker image to the server.

In summary, this Jenkinsfile defines a CI/CD pipeline that:
1. Builds a Docker image from the current directory.
2. Pushes the image to Docker Hub.
3. Uses Ansible to deploy the image to a server.

==================================ANSIBLE===================================

```yaml
---
- hosts: webserver
  become: true
  tasks:
    - name: Delete old Docker image
      shell: "sudo docker rmi renckel/fastapi-for-ci-cd:latest || true"

    - name: Pull Docker image
      shell: "sudo docker pull renckel/fastapi-for-ci-cd:latest"
    
    - name: Remove old container  
      shell: "sudo docker rm target-project-old || true"

    - name: Stop latest container
      shell: "sudo docker stop target-project || true"

    - name: Rename latest container  
      shell: "sudo docker rename target-project target-project-old || true"

    - name: Run container
      shell: "sudo docker run --name target-project -p 80:80 -e MYSQL_USER='root' -e MYSQL_PASSWORD='31xLobOJO4fFUKE62oOFA8ev1jhFRq' -e MYSQL_HOST='mysql-server-container' -e MYSQL_PORT='3306' -e MYSQL_DB='devops_finaltask_db' -e JWT_SECRET='m9nrS3ZayDL08v43wKFDYn9tyNipVI' -d --network=target-app-net renckel/fastapi-for-ci-cd:latest"

    - name: Create DB
      shell: "sudo docker exec mysql-server-container mysql -u root --password=31xLobOJO4fFUKE62oOFA8ev1jhFRq -e 'create database devops_finaltask_db;' || true"

    - name: Update database
      shell: "sudo docker exec target-project alembic -c app/alembic.ini upgrade head"
```

This Ansible playbook is designed to manage Docker containers for a web application on a target server. Let's break down each section:

1. `hosts: webserver`: 
   - This specifies that the playbook should run on hosts that are part of the `webserver` group in the Ansible inventory.

2. `become: true`: 
   - This ensures that the tasks are executed with elevated privileges (similar to using `sudo`).

3. `tasks`: 
   - This begins the list of tasks that will be executed on the target hosts.

4. `Delete old Docker image` task:
   - This task removes the specified Docker image if it exists. The `|| true` ensures that the command succeeds even if the image doesn't exist, preventing the playbook from failing at this step.

5. `Pull Docker image` task:
   - This task pulls the latest version of the specified Docker image from Docker Hub.

6. `Remove old container` task:
   - This task removes a container named `target-project-old` if it exists. This seems to be a cleanup step for any previously renamed containers.

7. `Stop latest container` task:
   - This task stops a running container named `target-project` if it's running.

8. `Rename latest container` task:
   - This task renames the `target-project` container to `target-project-old`. This is likely done to keep a backup of the previous container before deploying a new one.

9. `Run container` task:
   - This task runs a new Docker container with the specified image and settings. It maps port 80 inside the container to port 80 on the host, sets several environment variables (related to MySQL and JWT), and attaches the container to a network named `target-app-net`.

10. `Create DB` task:
   - This task executes a command inside the `mysql-server-container` to create a MySQL database. The `|| true` ensures that the command succeeds even if the database already exists.

11. `Update database` task:
   - This task runs the `alembic` command inside the `target-project` container to apply database migrations. Alembic is a database migration tool for SQLAlchemy, and this step ensures that the database schema is up-to-date with the latest changes.

In summary, this Ansible playbook manages the deployment of a Dockerized web application. It ensures that the old version of the application is properly stopped and backed up, deploys the latest version of the application, and manages the associated database.
