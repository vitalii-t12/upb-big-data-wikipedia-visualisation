# upb-big-data-wikipedia-visualisation

# Big Data Setup with Hadoop and Zeppelin

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Clone the repository](#clone-the-repository)
  - [Build and start the containers](#build-and-start-the-containers)
  - [Access the web interfaces](#access-the-web-interfaces)
  - [Use Zeppelin to interact with Hadoop](#use-zeppelin-to-interact-with-hadoop)


## Prerequisites
- Docker and Docker Compose installed.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd big-data-setup

2. Build and start the containers:

    ``` bash
    docker-compose up --build


3. Access the web interfaces:

- Hadoop Namenode UI: http://localhost:9870
- Zeppelin UI: http://localhost:8080

4. Use Zeppelin to interact with Hadoop via SQL or other interpreters.

    ```bash
    docker-compose up --build

# Hadoop configuration
To connect to Hadoop CLI from the terminal, you can use the following command:
   ```bash
     docker exec -it hadoop bash
  ```
To add hadoop user:
    ```bash
      adduser --disabled-password --gecos "" hadoop
     ```
Set apropriate permissions for the Hadoop directories:
   ```bash
    chown -R hadoop:hadoop /opt/hadoop
   ```