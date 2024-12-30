from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import config
import os
import cgi
import widget
import utils
from PIL import Image

logger = utils.getLogger()


class WeatherImageRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200) # 200 Ok: everything is okay
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _get_website(self):
        logger.info("Create website")
        app_options = ""
        app_str = ""

        for _app in config.apps:
            if str(_app) == config.active_app:
                logger.info(f"Set active app to {_app.id}")
                app_options += F'                    <option value="{_app.id}" selected>{_app.name}</option>\n'
            else:
                app_options += F'                    <option value="{_app.id}">{_app.name}</option>\n'

            app_str += F'            <details>\n'
            app_str += F'                <summary>{_app.name}</summary>\n'
            app_str += F'                <form action="{_app.id}" method="post">\n'
            app_str += F'                    <button class="btn_save" type="submit">Save</button>\n'
            app_str += F'                    <button class="btn_preview" type="button">Preview</button>\n'
            app_str += F'                    <fieldset>\n'
            app_str += F'                        <legend>General</legend>\n'
            for key, value in _app.general.items():
                app_str += F'                        <label>{key}: <input type="text" name="{key}" value="{value}"/></label><br/>\n'
            app_str += F'                    </fieldset>\n'
            app_str += F'                    <fieldset>\n'
            app_str += F'                        <legend>Parameter</legend>\n'
            for key, value in _app.parameter.items():
                app_str += F'                        <label>{key}: <input type="text" name="{key}" value="{value}"/></label><br/>\n'
            app_str += F'                    </fieldset>\n'
            app_str += F'                </form>\n'
            app_str += F'            </details>\n'

        # write website from template
        website = ""
        with open(os.path.join(os.path.dirname(__file__), 'template.html')) as file:
            website = file.read()
            website = website.replace("<INSERT_APPS>", app_str)
            website = website.replace("<INSERT_APP_OPTIONS>", app_options)

        return website

    def _read_post_query(self):
        # parse the data fields of post
        length = int(self.headers['Content-Length'])
        field_data = self.rfile.read(length)
        fields = parse_qs(field_data)
        fields = {key.decode(): val[0].decode() for key, val in fields.items()}
        logger.info(f"Received field keys: {fields.keys()}")
        return fields

    def do_Head(self):
        self._set_headers()

    def do_POST(self):
        if '/upload' in self.path:
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            try:
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                    fs_up = fs['upload']  # get content of form input with name "upload"
                    upload_image_path = os.path.join(os.path.dirname(__file__), 'upload.png')
                    logger.info(f"Upload image to {upload_image_path}")
                    with open(upload_image_path, 'wb') as file:
                        file.write(fs_up.file.read())
                    widget.update(upload_image_path)
                else:
                    logger.error("Unexpected POST request")
            except Exception:
                logger.error("File upload does not work", exc_info=True)

        elif '/general' in self.path:
            fields = self._read_post_query()
            if 'save' in fields.keys():
                logger.info('Button pressed in form "general"->"save"')
                config.active_app = fields.get('active_app', '')
            elif 'update' in fields.keys():
                logger.info('Button pressed in form "general"->"update"')
                widget.update()
            else:
                logger.warning('Should not happen in form "general"!')
        else:
            app_id = self.path.replace('/', '')
            app = config.get_app(app_id)

            if app:
                params = self._read_post_query()
                logger.info(f"Valid app found: {app_id}")
                app.parameter = params
                app.general = params
            else:
                logger.warning('Invalid App Requested! app_id: {app_id}')

        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))

    def do_GET(self):
        logger.info(f"Website Root is requested")
        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))


def create_server(ip_address="0.0.0.0", port=8000):
    handler = WeatherImageRequestHandler
    server_address = (ip_address, port)
    httpd = HTTPServer(server_address, handler)
    httpd.timeout = 300  # increase timeout for slow slicer
    logger.info(f"Open Browser: {utils.get_network_ip()}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    try:
        create_server()
    except ConnectionAbortedError:
        logger.error("Shit happens", exc_info=True)
        create_server()
