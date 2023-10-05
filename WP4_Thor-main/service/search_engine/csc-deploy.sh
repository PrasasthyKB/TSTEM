#!/bin/bash

# Replace the following variables with your server information
SERVER_USERNAME="ubuntu"
SERVER_IP="195.148.30.86"
REMOTE_DIRECTORY="/home/ubuntu/search_engine"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Replace "local_directory" with the path to the directory containing your code
LOCAL_DIRECTORY="/home/ubuntu/WP4_Thor/service/search_engine"

# Replace "your_ssh_private_key" with the path to your SSH private key
SSH_PEM_FILE="/home/ubuntu/thor-csc-elk.pem"

function zip_files() {
    echo "Zipping files..."
    cd "$LOCAL_DIRECTORY" || exit
    sudo apt install zip unzip
    sudo zip -r file.zip .
    echo "Files zipped!"
}

# Function to upload the zip file via SSH using PEM file
function upload_files() {
    echo "Uploading zip file to the server..."
    ssh -i "$SSH_PEM_FILE" "$SERVER_USERNAME@$SERVER_IP" "
        mkdir search_engine
    "
    scp -i "$SSH_PEM_FILE" file.zip "$SERVER_USERNAME@$SERVER_IP:$REMOTE_DIRECTORY/file.zip"
    echo "Upload completed!"
}

# Function to SSH into the server, unzip the file, and run docker-compose up
function run_docker_compose() {
    echo "Connecting to the server and setting up..."
    ssh -i "$SSH_PEM_FILE" "$SERVER_USERNAME@$SERVER_IP" "
        sudo apt install unzip
        cd $REMOTE_DIRECTORY
        unzip -o file.zip
        docker-compose -f $DOCKER_COMPOSE_FILE up --build -d
    "
    echo "Docker Compose up completed on the server!"
}

# Main script execution
zip_files || exit 1
upload_files || exit 1
run_docker_compose || exit 1
