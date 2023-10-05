import datetime
import json


class SearchResponseModel:
    ioc_source: str = None
    spider_name: str = None
    value: str = None
    type: str = None
    score: float = None

    def __init__(self, score, ioc_source, spider_name, value, type):
        self.score = score
        self.ioc_source = ioc_source
        self.spider_name = spider_name
        self.value = value
        self.type = type


class SearchFileResponseModel:
    id: str = None
    size: int = None
    mime_type: str = None
    first_seen: datetime = None
    feed_name: str = None
    score: float = None
    json: str = None

    def __init__(self, score, size, mime_type, first_seen, feed_name, json_, id):
        self.score = score
        self.size = size
        self.mime_type = mime_type
        self.first_seen = datetime.datetime.fromisoformat(first_seen)
        self.feed_name = feed_name
        self.json = json.dumps(json_, indent=4)
        self.id = id


class UrlFieldsResponseModel:
    community: object = None
    crawled: object = None

    def __init__(self, community=None, crawled=None):
        self.community = community
        self.crawled = crawled

    def to_dict(self):
        return self.__dict__


class GenericResponseModel:
    ip: str = None
    first_seen: datetime = None
    path: str = None
    port: str = None
    scheme: str = None,
    source: str = None,

    def __init__(self, source=None, ip=None, first_seen=None, path=None, port=None, scheme=None):
        self.source = source
        self.ip = ip
        self.first_seen = first_seen
        self.path = path
        self.port = port
        self.scheme = scheme

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        # Create a new dictionary to hold the attributes
        json_dict = self.__dict__.copy()

        # Convert the datetime object to a string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
        if isinstance(json_dict['first_seen'], datetime.datetime):
            json_dict['first_seen'] = json_dict['first_seen'].isoformat()

        # Serialize the dictionary to JSON format
        return json.dumps(json_dict)

    def format_first_seen(self):
        # Check if self.first_seen is a datetime object
        print("Type of first_seen record", type(self.first_seen))

        if isinstance(self.first_seen, datetime.datetime):
            # Format the datetime object to the desired format
            formatted_date = self.first_seen.strftime("%d %b %Y")
            return formatted_date
        else:
            return None


class CrawlerResponseModel:
    first_seen: datetime = None
    source: str = None
    value: str = None

    def __init__(self, first_seen=None, source=None, value=None):
        self.first_seen = first_seen
        self.source = source
        self.value = value


class FileFieldsResponseModel:
    source: str = None,
    first_seen: datetime = None
    size: int = None
    hash: list = None
    type: str = None
    imphash: str = None

    def __init__(self, source=None, first_seen=None, size=None, hash=None, type=None, imphash=None):
        self.source = source
        self.first_seen = first_seen
        self.size = size
        self.hash = hash
        self.type = type
        self.imphash = imphash

    def to_dict(self):
        return self.__dict__


class EmailFieldsResponseModel(json.JSONEncoder):
    first_seen: datetime = None
    source: str = None
    value: str = None

    def __init__(self, first_seen=None, source=None, value=None):
        self.first_seen = first_seen
        self.source = source
        self.value = value

    def to_dict(self):
        return self.__dict__


class WrapperModel(json.JSONEncoder):
    total: int = None
    page: str = None
    records: list[object] = None

    def __init__(self, total=None, page=None, records=None):
        self.total = total
        self.page = page
        self.records = records

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_dict(self):
        return self.__dict__

