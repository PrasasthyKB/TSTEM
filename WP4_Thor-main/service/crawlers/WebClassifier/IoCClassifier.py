import json
import os
import datetime
import time
from uuid import uuid4

from utils import extract_iocs

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

#import Text_classification #changing the model to longformer
import PyTorchPageClassPredicition

KAFKA_SERVER = os.environ["KAFKA_SERVER"]
KAFKA_TOPIC_CLEAR_WEB = "IoC_ClearWeb_Crawled"
KAFKA_TOPIC_DARK_WEB = "IoC_DarkWeb_Crawled"
KAFKA_CONSUMER_GROUP = "WebClassifier"
ELASTICSEARCH_SERVER = os.environ["ELASTICSEARCH_SERVER"]
ELASTICSEARCH_PASSWORD = os.environ["ELASTICSEARCH_PASSWORD"]
ES_INDEX_NAME= "web-latest"

if __name__ == "__main__":
    consumer = KafkaConsumer(
        KAFKA_TOPIC_CLEAR_WEB,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id=KAFKA_CONSUMER_GROUP,
    )

    consumer.subscribe([KAFKA_TOPIC_CLEAR_WEB,KAFKA_TOPIC_DARK_WEB])

    es = Elasticsearch(
        ELASTICSEARCH_SERVER, basic_auth=("elastic", ELASTICSEARCH_PASSWORD)
    )

    #classifier_instance = Text_classification.load() #changing the model to longformer
    classifier_instance = PyTorchPageClassPredicition.load()

    while True:
        raw_messages = consumer.poll(
                timeout_ms=10000, max_records=200
            )
        for topic_partition, messages in raw_messages.items():

            webpage_source = ""
            # if message topic is clear web
            if topic_partition.topic == KAFKA_TOPIC_CLEAR_WEB:
                webpage_source = "Clear_Web"
            # if message topic is dark web
            elif topic_partition.topic == KAFKA_TOPIC_DARK_WEB:
                webpage_source = "Dark_Web"

            for data in messages:
                text = data.value["text"]
                #pred = classifier_instance.classify_text(text) #changing the model to longformer
                st = time.time()
                pred = classifier_instance.page_class_predict(text)
                et = time.time()

                classification_time = et - st

                # Create payload for elasticsearch and add metadata
                payload = {
                    key: data.value[key] for key in ["url", "spider_name", "date_inserted"]
                }
                # Make sure date_inserted is in iso_format
                payload["date_inserted"] = datetime.datetime.fromisoformat(
                    payload["date_inserted"]
                ).isoformat()
                payload['@timestamp'] = datetime.datetime.now().replace(microsecond=0).isoformat()

                payload["webpage_source"] = webpage_source
                payload["classification_time"] = classification_time
                payload["document_length"] = len(text.split())
                payload["relevant"] = False
                payload["iocs"] = []

                if pred:
                    print("Found relevant web page. Attempting to extract IoCs...")
                    payload["relevant"] = True

                    st = time.time()
                    iocs = extract_iocs(text, data.value["url"])
                    et = time.time()
                    ioc_extraction_time = et - st
                    
                    payload["ioc_extraction_time"] = ioc_extraction_time
                    # Skip if no iocs found
                    print("Sending data to ElasticSearch.")

                    payload["iocs"] = iocs

                json_payload = json.dumps(payload)
                json_payload = str.encode(json_payload)

                try:
                    res = es.index(
                        index=ES_INDEX_NAME,
                        id=str(uuid4()),
                        document=json_payload,
                    )
                except Exception as e:
                    print("Error : ", e)
