# Thor documentation 
The repo hosts all the required scripts and documentation related to WP deliverables.

## THOR data collection capabilities

- Tier 1 Social Media
- Tier 2 Web crawling
- Tier 3 Honeypots
- Tier 4 Community feeds

<img width="958" alt="Screenshot 2022-08-15 at 17 08 44" src="https://user-images.githubusercontent.com/19819500/184651566-be6eb374-4d76-4645-ba29-3d8a1924a8f0.png">

## Software and libraries used

In this section we present the software that we have developed for each tier. Below we provide a tentative list is of the core framworks and libraries that we have used:
- Tweepy (4.6.0), which is a python library and enables us to use Twitter API. 
- Kafka-python (2.0.2) along with Flask (2.0.3), which handles large data processing and resolves bottlenecks.
- Pytorch (1.11.0), which helps us to classify tweets (This is not mandatory to use as we have already trained our model).
- Bentoml (0.11.0), which enables us to modularize our trained model for further use in our pipeline.
- Iocextractor (1.13.1), which helps us to not only extract the IoC’s but also convert them to their original format using regular expression rules.
- Elasticsearch (8.2.0), which enables us to index our final data.
- Docker (5.0.3) to pack everything together and offer a microservice that works independently.
- Terraform (1.1.3) and Ansible (ansible 5.8.0, ansible-core 2.12.6) for provisioning the underlaying infrastructure. 

## THOR data collection UI

* Pending, using Dialog Tool in Linux.

## Setting up

The points listed below only need to be performed once.
More comprehensive guide about Ansible and Terraform are located on `ansible` and `terraform` folder.

### AWS CLI

First, download configure AWS CLI by following [the official guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).
This step is required when you are planning to make any adjustment on resources on Terraform.

In short: download the binary, open terminal, configure the access by executing `aws configure`.

### Ansible

Install `ansible` and `ansible-playbook` to automate the process of configuring different aspect of VMs, such as installing dependencies and uploading crawler code.
Create virtual environment for installing `ansible` and its dependencies in isolation.

POSIX (bash/zsh):
```sh
python3 -m venv .env
source .env/bin/activate
```

Windows (PowerShell):
```powershell
python3 -m venv .env
.env\bin\Activate.ps1
```

For more information, please refer [official guide](https://docs.python.org/3/library/venv.html#creating-virtual-environments).

Finally, install `ansible` by executing `pip install -r requirements.txt`.

### Terraform

At the time of this writing, the used Terraform version is [v1.1.3](https://releases.hashicorp.com/terraform/1.1.3/).
Put the binary file somewhere recognizable by your terminal.

For an example of end-to-end integration from Terraform to Ansible, please refer [pull#3](https://github.com/IDUNN-project/WP4_Thor/pull/3).
