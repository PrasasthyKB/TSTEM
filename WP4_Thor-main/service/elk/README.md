# ELK Stack

The content here is derived from MIT-licensed [docker-elk](https://github.com/deviantony/docker-elk) with some modifications.

~~TODO: Logstash seems to have 403 issue connecting to Elasticsearch. [Similar thread](https://github.com/deviantony/docker-elk/issues/711).~~ =>
Create or adjust the `logstash_writer` role as written on [this page](https://www.elastic.co/guide/en/logstash/current/ls-security.html#ls-http-auth-basic) according to `./setup/roles/logtash_writer.json` file.

## Change Password

Note: if you change the password, then you need to update other services that rely on Elasticsearch.
*Typically* you just need to change environment variable or `.env` file for your service and rebuild.
```bash
sudo docker-compose up -d --build
```

If we ever need this, to change the password, first we need to get inside the ELK VM.
Assuming we are on the repository root directory:
```bash
ssh <username>@<public-ip> -i <private-key.pem>
```

Reset passwords for the default users.
The commands below resets the passwords of the elastic, logstash_internal and kibana_system users.
Take note of them.
```bash
sudo docker-compose exec elasticsearch bin/elasticsearch-reset-password --batch --user elastic
sudo docker-compose exec elasticsearch bin/elasticsearch-reset-password --batch --user logstash_internal
sudo docker-compose exec elasticsearch bin/elasticsearch-reset-password --batch --user kibana_system
```

Next, write the updated password into `.env` file inside the VM and [AWS Secrets Manager](https://eu-central-1.console.aws.amazon.com/secretsmanager/listsecrets?region=eu-central-1).

Rebuild Logstash and Kibana.
```bash
sudo docker-compose up -d --build logstash
sudo docker-compose up -d --build kibana
```

More detailed guide is available [here](https://github.com/deviantony/docker-elk#setting-up-user-authentication).
