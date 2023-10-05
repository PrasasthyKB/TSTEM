# WikiJS

This folder contains Wiki service which can be accessed (at the time of this writing with commit hash [583853a](https://github.com/IDUNN-project/WP4_Thor/tree/583853a)) at [http://18.198.4.60](http://18.198.4.60).

## Deployment

To deploy this service and restore from previous backup:

Go to `terraform` folder.
```bash
cd terraform
```

Generate the required files. `hosts_ini` for Ansible inventory and `wikijs_env` which holds credentials required for WikiJS.

```bash
terraform apply -var-file=cluster.tfvars -target="local_sensitive_file.hosts_ini" -target="local_sensitive_file.wikijs_env"
```

Since we are going to restore, we need to download the latest backup file that have been created before.
The files are available on [S3](https://s3.console.aws.amazon.com/s3/buckets/thor-infra?region=eu-central-1&prefix=wikijs/&showversions=false).
Copy `wiki-pg-xxx.dump` (database) to `<root-folder>/service/wikijs` on your local workstation.

Execute Ansible playbook to install Docker and upload the files.
```bash
cd ../ansible

# execute playbook
ansible-playbook wikijs.yml -i inventory/hosts.ini
```

Now, to restore the database and files, we need to SSH to WikiJS VM.
```bash
ssh <username>@<public-ip> -i <private-key.pem>
```

Where `username` is the default username (for Ubuntu VM it is usually `ubuntu`) and `public-ip` can be seen from `<root-folder>/ansible/inventory/hosts.ini` or AWS console.

Go to `wikijs` folder, restore the database.
```bash
cd wikijs # or wherever the folder is located

# start only the database
sudo docker-compose up -d db

# wipe the wiki db so it is fresh
sudo docker exec -it db dropdb -U wiki wiki
sudo docker exec -it db createdb -U wiki wiki

# restore the database, may take some time
cat wiki-pg-xxx.dump | sudo docker exec -i db pg_restore -U wiki -d wiki

# now start the WikiJS
sudo docker-compose up -d

# make sure everything is running properly
sudo docker-compose ps
```

Now, we can exit from terminal and open the Wiki by opening the VM's **public** IP.

## Backing up

The guide in this section is derived from [official transfer guide](https://docs.requarks.io/en/install/transfer). Check it for more information.

Because [all content is stored in the database](https://docs.requarks.io/storage), we need only need to backup database.
Similar with deployment, we need to get inside the VM.

```bash
ssh <username>@<public-ip> -i <private-key.pem>
```

Go to the folder where WikiJS is located.
```bash
cd wikijs

# backup database
sudo docker exec db pg_dump wiki -U wiki -F c > wikibackup.dump
```

Now, download the backup either via FileZilla, `scp`, or other similar tools.
And please, back the-backup-file up somewhere safe, like S3.
