
# Run the code in dev mode
Please go `./search_engine/server/src` and run the following command: 
```
flask --app app --debug run --port=5000
```


# Set .env file
Go to `./src` and create this template:
```
ELASTICSEARCH_SERVER='http://ELASTIC_URL/'
ELASTICSEARCH_PASSWORD='ELASTIC_PASSWORD'
API_PREFIX='/PREFIX/api' # If you want to deploy the app on sub path of a domain 
OPENAI_API_KEY='sk-...'
OPENAI_ORGANIZATION_ID='org-...'
MONGO_SERVER='localhost' # The name of the service in docker compose
MONGO_PORT='27017'
MONGO_ROOT_USERNAME='admin'
MONGO_ROOT_PASSWORD='1234'
MONGO_DATABASE='search_engine'
JWT_SECRET_KEY='1234...' 
JWT_ACCESS_TOKEN_EXPIRES='7' # days
```

In order to create `JWT_SECRET_KEY` please execute these lines of codes in python:
```
>>> import secrets
>>> secrets.token_hex(16)
```
The result should be something like `'38dd56f56d405e02ec0ba4be4607eaab'`

