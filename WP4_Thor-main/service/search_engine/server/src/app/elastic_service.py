from elasticsearch import Elasticsearch
import json
from datetime import datetime, timedelta
import os
import re

from app.models import GenericResponseModel, FileFieldsResponseModel, EmailFieldsResponseModel


class ElasticService:
    def __init__(self):
        client = Elasticsearch(
            os.environ['ELASTICSEARCH_SERVER'],
            basic_auth=('elastic', os.environ['ELASTICSEARCH_PASSWORD'])
        )
        self.client = client

    def search_url(self, term, offset, size):
        last_date = datetime.today() - timedelta(days=30)
        last_date_str = last_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if check_url_or_ip(term) == "ip":
            result = self.merged_url_search(offset, size, ip=term, from_date=last_date_str)
            return result

        if check_url_or_ip(term) == "url":
            print(term)
            result = self.merged_url_search(offset, size, url=term, from_date=last_date_str)
            return result

        return ([], 0)

    def search_file(self, file, offset, size):
        last_date = datetime.today() - timedelta(days=30)
        last_date_str = last_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if file is None:
            file = ""
        print(file)
        result = self.api_file_search(offset, size, hash=file, from_date=last_date_str)
        return result

    def api_url_search(self, offset=1, size=50, source=None, ip=None, port=None, url=None, from_date=None,
                       to_date=None):
        result = self.merged_url_search(offset, size, source, ip, port, url, from_date, to_date)
        return result

    def merged_url_search(self, offset=1, size=50, source=None, ip=None, port=None, url=None, from_date=None,
                          to_date=None):
        last_date = datetime.today() - timedelta(hours=24)

        query = '{ "bool":{ "should":[ { "match": { "threat.indicator.type": "url" } }, { "bool":{ "should":[ { ' \
                '"match_phrase":{ "type":"ipv4" } }, { "match_phrase":{ "type":"url" } } ], "minimum_should_match":1 ' \
                '} } ], "minimum_should_match":1 '

        must_query = []

        if source == "community":
            must_query.append('{ "query_string":{ "query":".ds-filebeat*", "fields":[ "_index" ] } }')

        elif source == "twitter":
            must_query.append('{ "query_string":{ "query":"Twitter", "fields":[ "ioc_source" ] } }')

        elif source == "clear_web":
            must_query.append('{ "match_phrase": {"ioc_source": "Clear_Web" }}')

        elif source == "dark_web":
            must_query.append('{ "query_string":{ "query":"Dark_Web", "fields":[ "ioc_source" ] } }')

        if ip:
            must_query.append(
                '{ "bool": { "must": [ { "query_string": { "query": "' + ip + '" , "fields": [ "threat.indicator.ip", "value"]}}]}}')

        if url:
            # url = url.replace(':', '\\\:').replace('/', '\\\/').replace('.', '\\\.')
            print(url)
            must_query.append(
                '{ "bool": { "should": [ { "match_phrase": {"threat.indicator.url.original": "' + url + '" }}, { "match_phrase": {"value": "' + url + '" }}], "minimum_should_match":1}}')

        if port:
            must_query.append('{ "match": { "threat.indicator.url.port": "' + port + '" } }')

        if 0 < len(must_query):
            query += ', "must": [' + ','.join(must_query) + ']'

        range_query = []
        if from_date or to_date:
            if from_date:
                range_query.append('"gte": "' + from_date + '"')
            if to_date:
                range_query.append('"lte": "' + to_date + '"')
        else:
            range_query.append('"gte": "' + last_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '"')

        print(', '.join(range_query))
        query += ',"filter": [ { "range": { "@timestamp": {' + ','.join(range_query) + '}}}]'

        query += '}}'

        print(query)

        response = self.client.search(
            index="filebeat*,logstash-ioc*,synthetic-iocs*",
            query=json.loads(query),
            from_=(offset - 1) * size,
            size=size,
            pretty=True,
            track_total_hits= 1000 # TODO
        )

        print("********** Got %d Hits! *********" % response['hits']['total']['value'])
        result = []
        if response.get('hits', None) is None:
            return None
        for hit in response['hits']['hits']:
            if 'filebeat' in hit['_index']:
                try:
                    record = GenericResponseModel()
                    newHit = hit["_source"]["threat"]["indicator"]

                    record.source = "community"
                    try:
                        record.ip = newHit["ip"]
                    except Exception:
                        pass

                    try:
                        record.first_seen = convert_date(newHit["first_seen"])
                    except Exception:
                        pass

                    try:
                        record.path = newHit["url"]["full"]
                    except Exception:
                        pass

                    try:
                        record.port = newHit["url"]["port"]
                    except Exception:
                        pass

                    try:
                        record.scheme = newHit["url"]["scheme"]
                    except Exception:
                        pass
                    result.append(record)

                except Exception as e:
                    print(str(e))

            if 'logstash-iocs' in hit['_index']:
                try:
                    record = GenericResponseModel()
                    newHit = hit["_source"]

                    try:
                        record.source = newHit["ioc_source"]
                    except Exception:
                        pass

                    if newHit['type'] == 'ipv4':
                        try:
                            record.ip = newHit["value"]
                        except Exception:
                            pass
                    try:
                        record.first_seen = convert_date(newHit["@timestamp"])
                    except Exception:
                        pass

                    if newHit['type'] == 'url':
                        try:
                            record.path = newHit["value"]
                        except Exception:
                            pass

                    result.append(record)

                except Exception as e:
                    print(str(e))

            if 'synthetic-iocs' in hit['_index']:
                try:
                    record = GenericResponseModel()
                    newHit = hit["_source"]

                    try:
                        record.source = newHit["ioc_source"]
                    except Exception:
                        pass

                    if newHit['type'] == 'ipv4':
                        try:
                            record.ip = newHit["value"]
                        except Exception:
                            pass
                    try:
                        record.first_seen = convert_date(newHit["@timestamp"])
                    except Exception:
                        pass

                    if newHit['type'] == 'url':
                        try:
                            record.path = newHit["value"]
                        except Exception:
                            pass

                    result.append(record)

                except Exception as e:
                    print(str(e))

        return (result, response['hits']['total']['value'])

    def api_file_search(self, offset=1, size=50, source=None, extension=None, hash=None, from_date=None, to_date=None):
        last_date = datetime.today() - timedelta(days=1)

        query = '{"bool":{ "should":[ { "match":{ "threat.indicator.type":"file" } }, { "match_phrase":{ "type":"hash" } } , { "match_phrase":{ "type":"md5_hash" } }, { "match_phrase":{ "type":"sha1_hash" } } ], "minimum_should_match":1'

        must_query = []

        if source == "community":
            must_query.append('{ "query_string":{ "query":".ds-filebeat*", "fields":[ "_index" ] } }')

        elif source == "twitter":
            must_query.append('{ "query_string":{ "query":"Twitter", "fields":[ "ioc_source" ] } }')

        elif source == "clear_web":
            must_query.append('{ "match_phrase": {"ioc_source": "Clear_Web" }}')

        elif source == "dark_web":
            must_query.append('{ "query_string":{ "query":"Dark_Web", "fields":[ "ioc_source" ] } }')

        if extension:
            must_query.append('{ "match": { "threat.indicator.file.type": "' + extension + '" } }')

        if hash:
            must_query.append(
                '{ "bool": { "should": [ { "query_string": { "query": "*' + hash + '*" , "fields": [ "value", "threat.indicator.file.hash.sha1", "threat.indicator.file.hash.tlsh", "threat.indicator.file.hash.md5", "threat.indicator.file.hash.sha256", "threat.indicator.file.hash.ssdeep"]}}]}}')

        if len(must_query) > 0:
            query += ', "must": [' + ','.join(must_query) + ']'

        range_query = []
        if from_date or to_date:
            if from_date:
                range_query.append('"gte": "' + from_date + '"')
            if to_date:
                range_query.append('"lte": "' + to_date + '"')
        else:
            range_query.append('"gte": "' + last_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '"')

        print(', '.join(range_query))
        query += ',"filter": [ { "range": { "@timestamp": {' + ','.join(range_query) + '}}}]'

        query += '}}'

        print("*** The query is: " + query)
        print(json.loads(query))
        response = self.client.search(
            index="filebeat*,logstash-ioc*,synthetic-iocs*",
            query=json.loads(query),
            from_=(offset - 1) * size,
            size=size,
            pretty=True
        )

        print("********** Got %d Hits! *********" % response['hits']['total']['value'])
        result = []
        if response.get('hits', None) is None:
            return None
        for hit in response['hits']['hits']:
            if 'filebeat' in hit['_index']:
                try:
                    record = FileFieldsResponseModel()
                    newHit = hit["_source"]["threat"]["indicator"]
                    record.source = "community"
                    try:
                        record.first_seen = convert_date(newHit["first_seen"])
                    except Exception:
                        pass

                    try:
                        record.size = newHit["file"]["size"]
                    except Exception:
                        pass

                    try:
                        record.imphash = newHit["file"]["pe"]["imphash"]
                    except Exception:
                        pass

                    try:
                        record.type = newHit["file"]["type"]
                    except Exception:
                        pass

                    try:
                        record.hash = newHit["file"]["hash"]
                    except Exception:
                        pass

                    result.append(record)

                except Exception as e:
                    print(str(e))

            if 'logstash-iocs' in hit['_index']:
                try:
                    record = FileFieldsResponseModel()
                    newHit = hit["_source"]

                    try:
                        record.source = newHit["ioc_source"]
                    except Exception:
                        pass

                    try:
                        record.first_seen = convert_date(newHit["@timestamp"])
                    except Exception:
                        pass

                    try:
                        record.hash = newHit["value"]
                    except Exception:
                        pass

                    result.append(record)

                except Exception as e:
                    print(str(e))

        return (result, response['hits']['total']['value'])

    def api_email_search(self, offset=1, size=50, source=None, phrase=None, from_date=None, to_date=None):
        last_date = datetime.today() - timedelta(days=1)

        query = '{ "bool": { "must": [ { "match_phrase": { "type": "email"} }'

        if source == "twitter":
            query += ',{ "query_string":{ "query":"Twitter", "fields":[ "ioc_source" ] } }'

        elif source == "clear_web":
            query += ',{ "match_phrase": {"ioc_source": "Clear_Web" }}'

        elif source == "dark_web":
            query += ',{ "query_string":{ "query":"Dark_Web", "fields":[ "ioc_source" ] } }'

        if phrase:
            query += ',{ "bool": { "should": [ { "query_string": { "query": "*' + phrase + '*" , "fields": [ "value"]'
            query += '}}]}}'

        query += '],'

        range_query = []
        if from_date or to_date:
            if from_date:
                range_query.append('"gte": "' + from_date + '"')
            if to_date:
                range_query.append('"lte": "' + to_date + '"')
        else:
            range_query.append('"gte": "' + last_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') + '"')

        print(', '.join(range_query))
        query += '"filter": [ { "range": { "@timestamp": {' + ','.join(range_query) + '}}}]'

        query += '}}'

        print("*** The query is: " + query)
        print(json.loads(query))
        print(type(offset))
        print(type(size))
        response = self.client.search(
            index="logstash-iocs-stream",
            query=json.loads(query),
            from_=(offset - 1) * size,
            size=size,
            pretty=True
        )

        print("********** Got %d Hits! *********" % response['hits']['total']['value'])
        result = []
        if response.get('hits', None) is None:
            return None
        for hit in response['hits']['hits']:
            try:
                record = EmailFieldsResponseModel()
                newHit = hit["_source"]

                try:
                    record.first_seen = convert_date(newHit["@timestamp"])
                except Exception:
                    pass

                try:
                    record.source = newHit["ioc_source"]
                except Exception:
                    pass

                try:
                    record.value = remove_username_from_email(newHit["value"])
                except Exception as e:
                    print(str(e))

                result.append(record)

            except Exception as e:
                print(str(e))

        return (result, response['hits']['total']['value'])


def remove_username_from_email(email):
    """
    Removes the username part from an email address and returns the domain part.
    """
    if "@" in email:
        # Split the email address by "@" character
        parts = email.split("@")
        # Return the domain part (last part of the split)
        return parts[-1]
    else:
        # If "@" is not present in the email address, return the original email
        return email


def check_url_or_ip(term):
    # Regular expression patterns for URL and IP address
    url_pattern = re.compile(r'^(?:https?://|http://)(?:\w+.)?[\w.-]+.\w+(?:/\S*)?$')
    ip_pattern = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')

    if url_pattern.match(term):
        return "url"
    elif ip_pattern.match(term):
        return "ip"
    else:
        return "Not a valid URL or IP address"


def convert_date(date_str):
    try:
        # Assuming the input string is in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
        datetime_obj = datetime.fromisoformat(date_str)
        return datetime_obj
    except ValueError:
        return "Invalid date format. Please provide the date in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
