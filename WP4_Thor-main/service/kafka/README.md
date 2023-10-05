# Kafka

This folder contains the definition of Kafka and several other supporting tools like Kafdrop.

## Change Default Password

By default, Kafdrop is not protected with basic authentication.
Since we are going to expose it to the Internet, it is a good idea to ***at least*** protect it with basic authentication.
In this deployment, the basic auth is provided by NGINX.

Before the deployment, we can generate the username and password first:
Assuming we are on the repository root directory:
```bash
# default username/password: goaway/hey-hey-changeme!
htpasswd -Bbn yourusernamehere passwordhere >| service/kafka/nginx.htpasswd
```

On Ubuntu, you can install `htpasswd` by executing `apt install apache2-utils`.


## Access

To access Kafdrop, open `http://<KAFKA_PUBLIC_IP>:31313` in a browser.
