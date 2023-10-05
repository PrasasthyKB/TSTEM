# Community Feed

We use Filebeat and its [Threat Intel module](https://www.elastic.co/guide/en/beats/filebeat/8.2/filebeat-module-threatintel.html) to collect feeds from different sources.
The results then will be directly written to Elasticsearch.

At the time of this writing, Filebeat gathers threat intel attributes from our own MISP instance.
The API key required by Filebeat has to be manually created on the MISP instance.
User can create a new one from `http://<misp-ip-address>/auth_keys/index` -> `Add authentication key`.

For more information about the MISP instance, please refer [the README file](../../misp/README.md).

## Deploy

To deploy Filebeat, user have to manually create MISP API key first.
Copy the API key and save it to [AWS Secrets Manager](https://eu-central-1.console.aws.amazon.com/secretsmanager/secret?name=thor-credentials&region=eu-central-1) with key `misp_api_key`.

Next, generate and ensure MISP API key is included the required `.env` file.
```sh
cd terraform
terraform apply -var-file=cluster.tfvars -target="local_sensitive_file.communityfeed_crawler_env"
```

Finally, go to `ansible` folder and deploy.
```sh
cd ../ansible
ansible-playbook communityfeed-crawler.yml -i inventory/hosts.ini
```
