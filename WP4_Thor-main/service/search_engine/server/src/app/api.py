from flask import Flask, jsonify, render_template, request, Response
from app.elastic_service import ElasticService
from flask import blueprints
from flask_jwt_extended import jwt_required

from app.models import WrapperModel
from app.conversation_manager import ConversationManager
from app import helper

bp = blueprints.Blueprint("se", __name__)

@bp.route('/home')
def index():
    print("Call index")
    service = ElasticService()
    url = request.args.get('url')
    file = request.args.get('file')
    if request.args.get('page'):
        page = int(request.args.get('page'))
        size = 10

    if url:
        results = service.search_url(url, page, size)
        return render_template('search.html', total=results[1], url_results=results[0], page=page)

    if file:
        results = service.search_file(file, page, size)
        return render_template('search.html', total=results[1], file_results=results[0], page=page)

    return render_template('search.html')

@bp.route('/api/urls', methods=["GET"])
@jwt_required()
def get_urls():
    service = ElasticService()
    if not request.args.keys():
        result = service.api_url_search(1, 50)
        wrapper = WrapperModel(result[1], 1, result[0])
        resp = Response(wrapper.to_json())
        resp.headers['Content-Type'] = 'application/json'
        return resp

    if 'ip' in request.args:
        ip = request.args['ip']
    else:
        ip = None

    if 'port' in request.args:
        port = request.args['port']
    else:
        port = None

    if 'source' in request.args:
        source = request.args['source']
    else:
        source = None

    if 'url' in request.args:
        url = request.args['url']
    else:
        url = None

    if 'from' in request.args:
        from_date = request.args['from']
    else:
        from_date = None

    if 'to' in request.args:
        to_date = request.args['to']
    else:
        to_date = None

    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1

    if 'size' in request.args:
        size = int(request.args['size'])
    else:
        size = 50

    result = service.api_url_search(page, size, source, ip, port, url, from_date, to_date)
    wrapper = WrapperModel(result[1], page, result[0])
    resp = Response(wrapper.to_json())
    resp.headers['Content-Type'] = 'application/json'
    return resp

@jwt_required()
@bp.route('/api/files', methods=["GET"])
def get_files():
    service = ElasticService()
    if not request.args.keys():
        result = service.api_file_search(1, 50)
        wrapper = WrapperModel(result[1], 1, result[0])
        resp = Response(wrapper.to_json())
        resp.headers['Content-Type'] = 'application/json'
        return resp

    if 'extension' in request.args:
        extension = request.args['extension']
    else:
        extension = None

    if 'hash' in request.args:
        hash = request.args['hash']
    else:
        hash = None

    if 'source' in request.args:
        source = request.args['source']
    else:
        source = None

    if 'from' in request.args:
        from_date = request.args['from']
    else:
        from_date = None

    if 'to' in request.args:
        to_date = request.args['to']
    else:
        to_date = None

    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1

    if 'size' in request.args:
        size = int(request.args['size'])
    else:
        size = 50

    result = service.api_file_search(page, size, source, extension, hash, from_date, to_date)
    wrapper = WrapperModel(result[1], page, result[0])
    resp = Response(wrapper.to_json())
    resp.headers['Content-Type'] = 'application/json'
    return resp


@bp.route('/api/email-domains', methods=["GET"])
def get_emails():
    service = ElasticService()
    if not request.args.keys():
        result = service.api_email_search(1, 50)
        wrapper = WrapperModel(result[1], 1, result[0])
        resp = Response(wrapper.to_json())
        resp.headers['Content-Type'] = 'application/json'
        return resp

    if 'phrase' in request.args:
        phrase = request.args['phrase']
    else:
        phrase = None

    if 'from' in request.args:
        from_date = request.args['from']
    else:
        from_date = None

    if 'source' in request.args:
        source = request.args['source']
    else:
        source = None

    if 'to' in request.args:
        to_date = request.args['to']
    else:
        to_date = None

    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1

    if 'size' in request.args:
        size = int(request.args['size'])
    else:
        size = 50

    result = service.api_email_search(page, size, source, phrase, from_date, to_date)
    wrapper = WrapperModel(result[1], page, result[0])
    resp = Response(wrapper.to_json())
    resp.headers['Content-Type'] = 'application/json'
    return resp


@bp.route('/api/chat', methods=["POST"])
def chat():
    message = request.json["message"]
    print(message)
    cv_manager = ConversationManager()
    response = cv_manager.do_asnwer(message)
    print(response)
    return {"message": response}


@bp.route('/api/config', methods=["GET"])
def get_config():        
    server, username , password = helper.get_wazuh_config()
    response_data = {
        "server": server,
        "username": username,
        "password": password
    }
    return jsonify(response_data)


@bp.route('/api/config', methods=["POST"])
def update_config():
    server = request.json["server"]
    username = request.json["username"]
    password = request.json["password"]
    try:
        helper.set_wazuh_config(server, username, password)
        return jsonify({"message": "Configuration updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})
