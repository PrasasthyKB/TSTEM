# Ansible

The resources declared here represents preparation, configuration, or deployment **inside a VM**.
Commonly, Ansible playbooks in this folder represents the deployment of services and installation of the dependencies: install `fail2ban`, `docker`, `docker-compose`, and uploading the services' code.
To know what Ansible is capable for, please refer [this guide](https://www.redhat.com/en/topics/automation/learning-ansible-tutorial) or official pages.

After creating the VM and related stuff via Terraform on your local workstation, a file named `ansible/inventory/hosts.ini` will be created.
If it is not, go to `terraform` folder and generate the required file.
```sh
cd ../terraform
terraform apply -var-file=cluster.tfvars -target="local_sensitive_file.hosts_ini"
```

If this is the first time you execute Ansible playbook:
1. Install dependency from Ansible galaxy via `ansible-galaxy install -r requirements.yml`.
2. **Before** connecting to a VM via SSH or executing Ansible playbook, please download the private key and put it on root folder of this project.

## Deploying services on top of VM

Assuming a VM is ready and user would like to deploy a particular service on top of the VM.
```sh
ansible-playbook wikijs.yml -i inventory/hosts.ini
```

If it fails, check what is the root cause.
To check whether a particular VM (or all) is problematic:
```sh
ansible -i inventory/hosts.ini -m ping all
```

The steps needed to deploy the services are generally the same (exceptions apply).
```sh
# make sure you are on <root-folder>/ansible

ansible-playbook clearweb-crawler.yml -i inventory/hosts.ini
ansible-playbook communityfeed-crawler.yml -i inventory/hosts.ini
ansible-playbook darkweb-crawler.yml -i inventory/hosts.ini
ansible-playbook elk.yml -i inventory/hosts.ini
ansible-playbook kafka.yml -i inventory/hosts.ini
ansible-playbook misp.yml -i inventory/hosts.ini
ansible-playbook twitter-crawler.yml -i inventory/hosts.ini
ansible-playbook wikijs.yml -i inventory/hosts.ini
```

For some services that requires files outside of this repository, the files have to be downloaded manually and put in correct folders.
The reason for this is because those external files can be anywhere, and the automated way to gather all of them are definitely out of the scope of this project.

At the time of this writing (commit hash [583853a](https://github.com/IDUNN-project/WP4_Thor/tree/583853a)), there are 3 services that require external files, and all of them are ML model:
1. Twitter crawler: [download here](https://s3.console.aws.amazon.com/s3/object/thor-infra?region=eu-central-1&prefix=TwitterCrawler/model.pt), save as `<root-folder>/service/crawlers/twitter/20220523165127_E8A2B3/Tweet_classification/artifacts/model.pt`.
2. Clear web crawler: [download here](https://s3.console.aws.amazon.com/s3/object/thor-infra?region=eu-central-1&prefix=DarkWebCrawler/crawl-models/model.pt), save as `<root-folder>/service/crawlers/ClearWeb/classifier/20220722161405_3179B2/PyTorchPageClassPredicition/artifacts/model.pt`.
3. Dark web crawler: [download here](https://s3.console.aws.amazon.com/s3/object/thor-infra?region=eu-central-1&prefix=DarkWebCrawler/crawl-models/model.pt), save as `<root-folder>/service/crawlers/DarkWeb/classifier/20220722161405_3179B2/PyTorchPageClassPredicition/artifacts/model.pt`.

After the required file(s) have been downloaded, continue with deploying the service using Ansible playbook, i.e. `ansible-playbook twitter-crawler.yml -i inventory/hosts.ini`.
