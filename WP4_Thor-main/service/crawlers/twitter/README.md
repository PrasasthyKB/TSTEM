# Twitter Crawler

To run the pipeline, first download the ML model [here](https://s3.console.aws.amazon.com/s3/object/thor-infra?region=eu-central-1&prefix=TwitterCrawler/model.pt), save as `<root-folder>/service/crawlers/twitter/20220523165127_E8A2B3/Tweet_classification/artifacts/model.pt`.

Now that ML model file is downloaded, simply run:

```bash
docker-compose up -d
```

And confirm whether the containers are running without issues:
```bash
docker-compose ps
```

## Dependencies

The crawler depends on several other services to work properly.
The services and usage locations are:
1. Elasticsearch:
   - `ELASTICSEARCH_SERVER` and `ELASTICSEARCH_PASSWORD` in `./app.py`
2. Kafka:
   - `KAFKA_SERVER` in `./app.py`
