from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

from app import create_app
load_dotenv()
app = create_app()
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
