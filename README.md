# Detect Sleep State
Detecting sleep states is essential for understanding sleep patterns and their impact on health, mood, and behavior. This competition, hosted by the Child Mind Institute, aims to develop models that detect sleep onset and wake times using wrist-worn accelerometer data.

## Overall Architecture
![overall-architecture](/assets/overall-architecture.png)

## Table of Contents

- [Detect Sleep State](#detect-dleep-state)
  - [Overall architecture](#overall-architecture)
  - [Table of Contents](#table-of-contents)
  - [Development stage](#development-stage)
    - [1. Set up](#1-set-up)
      - [1.1. Set up environments (poetry)](#11-set-up-environments-poetry)
      - [1.2. Install docker](#12-install-docker)
      - [1.3. Create a project in Google Cloud Platform (GCP)](#13-create-a-project-in-google-cloud-platform-gcp)
      - [1.4. Install and setup Google Cloud CLI](#14-install-and-setup-google-cloud-cli)
    - [2. Data preparation](#2-data-preparation)
      - [2.1. Download data](#21-download-data)
      - [2.2 Merge data](#22-merge-data)
    - [3. Explore data analysis (EDA) and Baseline](#3-explore-data-analysis-eda-and-baseline)
    - [4. Train](#4-train)
      - [4.1. Set up MLflow Server](#41-set-up-mlflow-server)
        - [4.1.1. Access MinIO UI](#411-access-minio-ui)
        - [4.1.2. Spin up MLflow tracking server](#412-spin-up-mlflow-tracking-server)
      - [4.2. Train model](#42-train-model)
    - [5. Deploy FastAPI and Docker Image](#5-deploy-fastapi-and-docker-image)
    - [6. Jenkins](#6-jenkins)
        - [6.1. Install Ngrok](#61-install-ngrok)
        - [6.2. Set up Jenkins](#62-set-up-jenkins)
            - [6.2.1. Run Jenkins Docker container](#621-run-jenkins-docker-container)
            - [6.2.2. Install Docker Plugins in Jenkins](#622-install-docker-plugins-in-jenkins)
            - [6.2.3. Make locally hosted Jenkins accessible from outside your network using Ngrok](#623-make-locally-hosted-jenkins-accessible-from-outside-your-network-using-ngrok)
            - [6.2.4. Add Jenkins to Github Webhooks](#624-add-jenkins-to-github-webhooks)
            - [6.2.5. Generate personal access tokens (classic)](#625-generate-personal-access-tokens-classic)
            - [6.2.6. Configure](#626-configure)
  - [Production stage](#production-stage)
    - [7. Set up](#7-set-up)
      - [7.1. Set up GCP](#71-set-up-gcp)
        - [7.1.1. Create a project in GCP](#711-create-a-project-in-gcp)
        - [7.1.2. Enabling the Kubernetes Engine API](#712-enabling-the-kubernetes-engine-api)
        - [7.1.3. Install and setup Google Cloud CLI](#713-install-and-setup-google-cloud-cli)
        - [7.1.4. Install gke-cloud-auth-plugin](#714-install-gke-cloud-auth-plugin)
        - [7.1.5. Create a service account](#715-create-a-service-account)
      - [7.2. Install terraform](#72-install-terraform)
      - [7.3. Install kubectl, kubectx and kubens](#73-install-kubectl-kubectx-and-kubens)
      - [7.4. Install helm](#74-install-helm)
      - [7.5. Connect to a Google Kubernetes Engine (GKE) cluster](#75-connect-to-a-google-kubernetes-engine-gke-cluster)
        - [7.5.1. Create the GKE cluster](#751-create-the-gke-cluster)
        - [7.5.2. Connect to the GKE cluster](#752-connect-to-the-gke-cluster)
    - [8. Deploy to GKE](#8-deploy-to-gke)
      - [8.1. Deploy Nginx Service Controller](#81-deploy-nginx-service-controller)
      - [8.2. Deploy application service](#82-deploy-application-service)
      - [8.3. Deploy monitoring service](#83-deploy-monitoring-service)

## Development Stage


### 1. Setup


#### 1.1. Set up environments (poetry)
1. Installation 
- Open Terminal (on macOS and Linux) or PowerShell (on Windows) and execute the following command:

- The cmd bellow is for Linux OS:

```cmd
curl -sSL https://install.python-poetry.org | python3 -
poetry --version 
```
2. Setup new environment

- Install poetry environment from `pyproject.toml` and `poetry.lock`:
```cmd
poetry install
poetry lock
```


#### 1.2 Install docker
Install docker as instructions: [Docker installation](https://docs.docker.com/engine/install/)

We also push images to Docker Hub. You need to log in to Docker by using the following command:

```bash
docker login
```

You will be prompted to enter your Docker Hub username, password, and email address (optional). After successful authentication, you can proceed with your Docker tasks, such as pushing or pulling images from Docker Hub.

#### 1.3 Create a project in Google Cloud Platform (GCP)

* Sign in to the Google Cloud Console.
* Navigate to the project creation page by clicking on this link: [Create a project](https://console.cloud.google.com/projectcreate)
*Provide a name for your project.
* (Optional) Modify the project ID if necessary (must be unique across all GCP projects).
* Select the appropriate billing account. If you do not have one, you will need to create a billing account.
* (Optional) Choose an organization if required.
* Click Create to initialize the project.

After project creation, your project appears as follows:

![gcp-project-dashboard](/assets/gcp-project-dashboard.png)


#### 1.4. Install and setup Google Cloud CLI
To install the Google Cloud (gcloud) CLI, follow the instructions in this official guide: [Gcloud CLI Installation](https://cloud.google.com/sdk/docs/install). The gcloud CLI includes command-line tools such as **gcloud**, **gsutil**, and **bq** for managing various Google Cloud resources.

After installation, authenticate with Google Cloud to manage resources:

1. Log in to your Google Cloud account:
    ```bash
    gcloud auth login
    ```
    This command launches a browser window prompting you to log in. Follow the steps to complete authentication.

2. Authenticate your application’s default credentials:
    ```bash
    gcloud auth application-default login
    ```
    This step ensures that applications running locally can securely access Google Cloud services.

3. Initialize your Google Cloud configuration:
    ```bash
    gcloud init
    ```
    This command helps configure your default project, region, and other settings necessary for interacting with Google Cloud from your local machine.

### 2. Data preparation

#### 2.1 Download data
You can download data from Kaggle: [Child mind institute: Detect Sleep State](https://www.kaggle.com/competitions/child-mind-institute-detect-sleep-states/data)
#### 2.2 Merge data
Because of my laptop only have CPU, so we can make the data smaller for this experiment. This `cmd` below also have a little bit feature engineering step.

```cmd 
make merge
```

### 3. Explore data analysis (EDA) and Baseline
You can refer to this notebook [baseline.ipynb notebook](/media/dattruong/568836F88836D669/dattruong/MLE/Project/Detect-sleep-states/notebooks/baseline.ipynb) to explore the baseline, possibly to gain a better understanding of the dataset's structure, contents, and any potential insights it may offer.
    
### 4. Train

#### 4.1. Set up MLflow Server
To track the training experiments, we'll spin up the MLflow server. The backend storage of this tracking server is Postgres and the artifact storage is MinIO. Before start up the server, we first need to generate `MINIO_ACCESS_KEY` and `MINIO_SECRET_ACCESS_KEY`.


##### 4.1.1. Access MinIO UI
```cmd
make minio-lcoal
```

The MinIO UI at `localhost:9001`:

![minio](/assets/minio.png)

The username and password are stored in the `.env` file. You can follow my [.env_example](/.env_example)

![envfile](/assets/envfile.png)

##### 4.1.2.  MLflow tracking server
The Mlflow UI at `localhost:5001`

```
make mlflow-local
```
![mlflow](/assets/mlflow.png)

#### 4.2 Train model

First, let's delve into some configurations for the training experiment.

You can make these params smaller for faster training in this experiment.

![params-training](/assets/params-training.png)

```cmd
make train
```

![mlflow-tracking](/assets/mlflow-tracking.png)

After training, you can see the experiment in the `localhost:5001`

### 5 Deploy FastAPI and Docker Image

Run the `cmd` below to build a Docker image for the FastAPI application.

```cmd
make build-app
```
Navigate to `http://localhost:8000` in your web browser to access your FastAPI app locally. You can send an image and get the predictions:


![local-app-fastapi](/assets/local-app-fastapi.png)

### 6. Jenkins

##### 6.1. Install Ngrok

- Follow the link to install Ngrok: [install ngrok](https://ngrok.com/download)
- Sign up for the account: [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
- Follow the instructions to add your authtoken.
![ngrok-jenkins](/assets/ngrok-jenkins.png)

##### 6.2. Set up Jenkins

###### 6.2.1. Run Jenkins Docker container

Run the following command to spin up Jenkins:

```bash
make jenkins
```

Next steps:

- Open your web browser and navigate to `http://localhost:8081`. You'll be prompted to unlock Jenkins by providing an initial admin password.
- Get initial admin password: To retrieve the initial admin password, run the following command in your terminal:

    ```bash
    docker exec jenkins-container cat /var/jenkins_home/secrets/initialAdminPassword
    ```

- Complete setup: Follow the on-screen instructions to complete the setup wizard. You can install recommended plugins or choose to install plugins later.
- Create an admin user: After plugin installation, create an admin user for Jenkins.
- Once the setup is complete, you can start using Jenkins.

###### 6.2.2. Install Docker Plugins in Jenkins

We will use Docker to run CI in Jenkins. Follow the steps below to install these plugins.

- Navigate to Jenkins Dashboard and go to **Manage Jenkins**.
- In the **Manage Jenkins** section, click on **Manage Plugins**.
- Navigate to the **Available** tab, which lists all available plugins that can be installed.
- Search for _Docker Pipeline_ and _Docker plugin_ and install them.
- Click on the "Install without restart" button. This will download and install the selected plugin(s) without requiring a Jenkins restart.

![Jenkins dasboard](/assets/jenkins-dashboard.png)

![install_plugins](/assets/install_plugins.png)
###### 6.2.3. Make locally hosted Jenkins accessible from outside your network using Ngrok

Run the following command:

```bash
ngrok http http://localhost:8081
```

###### 6.2.4. Add Jenkins to Github Webhooks

Once you've made your Jenkins instance accessible via Ngrok, you can configure GitHub webhooks to trigger Jenkins builds automatically whenever there are new commits or pull requests pushed to your repository.

- **Payload URL**: `Ngrok url` + `github-webhook/`. Example: `https://ac53-2405-4803-ed32-c86b-f737-d778.ngrok-free.app/github-webhook/`
- **Content type**: application/json
- **Let me select individual events**: pull requests, pushes

![webhooks](/assets/webhooks.png)
###### 6.2.5. Generate personal access tokens (classic)

![personal-access-tokens](/assets/personal-access-tokens.png)

###### 6.2.6. Configure

- Create the Multibranch Pipeline
    ![multibranch-pipeline](/assets/multibranch-pipeline.png)

- Configure the Multibranch Pipeline
    ![configuration-multibranch-pipeline](/assets/configuration-multibranch-pipeline.png)

- Add credential (personal access token) created at [Generate personal access tokens (classic)](#625-generate-personal-access-tokens-classic) to **Password**.
    ![github-credentials](/assets/github-credentials.png)
    ![final-configuration-multibranch-piplines](/assets/final-configuration-multibranch-pipline.png)


- Modify Github API usage rate limit
    ![api-usage-rate](/assets/api-usage-rate.png)

After completing the setup, every time you push or create a pull request, Jenkins will trigger and check your code quality (based on the rules in the [Jenkinsfile](Jenkinsfile)). If all checks pass, your push or pull request will proceed.




## Production Stage

### 7. Set up

#### 7.1. Set up GCP

##### 7.1.1. Create a project in GCP

Refer to [Create a project in Google Cloud Platform (GCP)](#13-create-a-project-in-google-cloud-platform-gcp) in development stage.

##### 7.1.2. Enabling the Kubernetes Engine API

Navigate to the following link to enable Kubernetes Engine API: [Kubernetes Engine API](https://console.cloud.google.com/apis/library/container.googleapis.com)
![kubernetes-engine-api](/assets/kubernetes-engine-api.png)

##### 7.1.3. Install and setup Google Cloud CLI

Refer to [Install and setup Google Cloud CLI](#14-install-and-setup-google-cloud-cli) in development stage.

##### 7.1.4. Install gke-cloud-auth-plugin

Run the following command in your terminal:

```bash
sudo apt-get install google-cloud-cli-gke-gcloud-auth-plugin
```

##### 7.1.5. Create a service account

- Navigate to [Service acounts](https://console.cloud.google.com/iam-admin/serviceaccounts) and click "CREATE SERVICE ACCOUNT".
- Select `Kubernetes Engine Admin` role.
- Create new key as json type for your service account. Download this json file and save it in [terraform/.credentials](production/terraform/.credentials) directory. Update **credentials** in [terraform/main.tf](production/terraform/main.tf) with your json directory.
- Navigate to [IAM](https://console.cloud.google.com/iam-admin/iam) and click on "GRANT ACCESS". Then, add new principals; this principal should be your service account. Finally, select the `Owner` role.

#### 7.2. Install terraform

- Download terraform as instructions via this link: [Download terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Get terraform version and update **required_version** in [terraform/main.tf](production/terraform/main.tf)


#### 7.3. Install kubectl, kubectx and kubens

Kubectl, kubectx, and kubens are tools that can help with navigating clusters and namespaces in Kubernetes. Kubectl is a command-line tool that can be used to deploy applications, inspect resources, and view logs. Kubectx and kubens can help with faster context switching, which can reduce the need for manual command modifications.

- Install kubectl: [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- Install kubectx and kubens: [kubectx and kubens](https://github.com/ahmetb/kubectx#manual-installation-macos-and-linux)

#### 7.4. Install helm

Helm helps you manage Kubernetes applications — Helm Charts help you define, install, and upgrade even the most complex Kubernetes application.

- Install helm: [helm](https://helm.sh/docs/intro/install/)

#### 7.5. Connect to a Google Kubernetes Engine (GKE) cluster

##### 7.5.1. Create the GKE cluster

Update your **project_id** in [terraform/variables.tf](production/terraform/variables.tf) and then, run the following command:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

The GKE cluster I configured has 1 node and its machine is "e2-standard-4" (4 CPU and 16 GB Memory)

![gke-cluster](/assets/gke-cluster.png)

##### 7.5.2. Connect to the GKE cluster

- Navigate to [GKE UI](https://console.cloud.google.com/kubernetes/list)
- Click on the vertical ellipsis icon and choose "Connect". A popup window will appear, displaying options to connect to the cluster as follow:

    ![gke-cluster-connect](/assets/gke-cluster-connect.png)


- Copy and run the command in the terminal:

    ```bash
    gcloud container clusters get-credentials [YOUR CLUSTER] --zone [YOUR REGION] --project [YOUR PROJECT ID]
    ```

- Check the connection from local using `kubectx`
![kubectx](/assets/kubectx.png)

### 8. Deploy to GKE
#### 8.1 Deploy Nginx Service Controller

The NGINX Ingress Controller is a widely used solution in Kubernetes environments for handling inbound traffic to applications within the cluster. It functions as a load balancer, directing external requests to the appropriate services inside the Kubernetes cluster based on predefined rules and configurations.

```cmd
cd helm_charts/nginx_ingress
kubectl create ns nginx-ingress 
kubens nginx-ingress 
helm upgrade --install nginx-ingress-controller .
```
#### 8.2 Deploy application service

```cmd
cd helm_charts/app
kubectl create ns model-serving
kubens model-serving
helm upgrade --install dss-app .
```
Wait several minutes until it deployed sucessfully.

Now, we will test the app, do the following steps:

- Obtain the IP address of nginx-ingress

    ```bash
    k get ing
    ```

- Add the domain name `detect-sleep-state.com` of this IP to /etc/hosts where the hostnames are mapped to IP addresses.

    ```bash
    sudo nano /etc/hosts
    [YOUR_INGRESS_IP_ADDRESS] detect-sleep-state.com
    ```

    Example:

    ```nano
    35.247.165.184 detect-sleep-state.com
    ```

- Open a web browser and navigate to `detect-sleep-state.com/docs` to access the FastAPI app. Now we can test the app
![dss-app-ingress](/assets/dss-app-ingress.png)



#### 8.3 Deploy monitoring service
We use `kube-prometheus-stack` to deploy a monitoring solution for the Kubernetes cluster. This stack, provided by the Prometheus community, includes various components such as Prometheus, Grafana, Alertmanager, and other Prometheus ecosystem tools configured to monitor the health and performance of your cluster's resources.


```cmd
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
cd helm_charts/kube-prometheus-stack
kubectl create ns monitoring
kubens monitoring
helm upgrade --install kube-grafana-prometheus .
```

Add all the services of the IP to /etc/hosts
```nano
sudo nano /etc/hosts
[YOUR_INGRESS_IP_ADDRESS] detect-sleep-state.com
[YOUR_INGRESS_IP_ADDRESS] grafana.monitor.com
[YOUR_INGRESS_IP_ADDRESS] prometheus.monitor.com
[YOUR_INGRESS_IP_ADDRESS] alert.monitor.com
```

example:
```
35.247.165.184 detect-sleep-state.com
35.247.165.184 grafana.monitor.com
35.247.165.184 prometheus.monitor.com
35.247.165.184 alert.monitor.com
```
![prometheus-execute](/assets/prometheus-execute.png)
![prometheus-execute-cpu](/assets/prometheus-execute-cpu.png)
![grafana-dashboard](/assets/grafana-dashboard.png)


