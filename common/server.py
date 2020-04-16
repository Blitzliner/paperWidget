from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import configparser
import logging
import os
import cgi
import widget

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)

class WeatherImageRequestHandler(BaseHTTPRequestHandler):#http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200) # 200 Ok: everything is okay
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_Head(self):
        self._set_headers()

    def _get_app_ids(self, app_main_path='../apps/'):
        # get all apps        
        app_main_path = os.path.join(os.path.dirname(__file__), app_main_path)

        return [d for d in os.listdir(app_main_path) if os.path.isdir(os.path.join(app_main_path, d))]
        
    def _get_website(self):
        logger.info("Create website")
        # read file structure and config files for building up the website
        app_main_path = os.path.join(os.path.dirname(__file__), "../apps/")
        
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(app_main_path, 'config.cfg'))
        active_app = cfg['general'].get('ActiveApp', '')
        
        # get all apps        
        app_dirs = [os.path.join(app_main_path, d) for d in os.listdir(app_main_path) if os.path.isdir(os.path.join(app_main_path, d))]
        
        app_options = ""
        app_str = ""
        
        for app_dir in app_dirs:
            cfg = configparser.ConfigParser()
            cfg.read(os.path.join(app_dir, 'config.cfg'))
            app_id = os.path.basename(app_dir)
            app_name = cfg['general'].get('app_name', "AppName")
            
            if (active_app == app_id):
                logger.info(F"Set active app to {active_app}")
                app_options += F'                    <option value="{app_id}" selected>{app_name}</option>\n'
            else:
                app_options += F'                    <option value="{app_id}">{app_name}</option>\n'
                
            app_str += F'            <details>\n'
            app_str += F'                <summary>{app_name}</summary>\n'
            app_str += F'                <form action="{app_id}" method="post">\n'
            app_str += F'                    <button class="btn_save" type="submit">Save</button>\n'
            app_str += F'                    <button class="btn_preview" type="button">Preview</button>\n'
            app_str += F'                    <fieldset>\n'
            app_str += F'                        <legend>General</legend>\n'
            
            for key, value in cfg.items('general'):
                app_str += F'                        <label>{key}: <input type="text" name="{key}" value="{value}"/></label><br/>\n'
                
            app_str += F'                    </fieldset>\n'
            app_str += F'                    <fieldset>\n'
            app_str += F'                        <legend>Parameter</legend>\n'
            
            for key, value in cfg.items('parameter'):
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
            
        return (website)
    
    def _update_active_app(self, app_name, config_file='../apps/config.cfg'):
        if len(app_name):
            cfg = configparser.ConfigParser()
            script_dir = os.path.dirname(__file__)
            config_filepath = os.path.join(script_dir, config_file)
            cfg.read(config_filepath)
            cfg['general']['ActiveApp'] = app_name
            with open(config_filepath, 'w') as file:
                cfg.write(file)
                
    def _update_app(self, app_id, query):
        # get config file with the app id
        cfg = configparser.ConfigParser()
        script_dir = os.path.dirname(__file__)
        config_file = os.path.join(script_dir, '../apps', app_id, 'config.cfg')
        cfg.read(config_file)
        
        for key, value in query.items():
            if cfg.has_option('general', key):
                logger.info(F"Update {key} with {value}")
                cfg.set('general', key, value)
            elif cfg.has_option('parameter', key):
                logger.info(F"Update {key} with {value}")
                cfg.set('parameter', key, value)
            else:
                logger.warning(F"Key not found: {key}")
        
        with open(config_file, 'w') as file:
            cfg.write(file)      
    def _read_post_query(self):
        # parse the data fields of post
        length = int(self.headers['Content-Length'])
        field_data = self.rfile.read(length)
        fields = parse_qs(field_data)
        fields = { key.decode(): val[0].decode() for key, val in fields.items() }
        logger.info(F"Received field keys: {fields.keys()}")
        return fields
        
    def do_POST(self):
        if '/upload' in self.path:
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            try:
                if ctype == 'multipart/form-data':  
                    fs = cgi.FieldStorage( fp = self.rfile, headers = self.headers, environ={ 'REQUEST_METHOD':'POST' })
                    fs_up = fs['upload'] # get content of form input with name "upload"
                    filepath = os.path.join(os.path.dirname(__file__), 'upload.png')
                    logger.info(F"Upload image to {filepath}")
                    with open(filepath, 'wb') as file:
                        file.write(fs_up.file.read())
                        
                    widget.update(filepath)
                else: 
                    logger.error("Unexpected POST request")
            except Exception as e:
                logger.error(e)
           
        elif '/general' in self.path:
            fields = _read_post_query()
            if 'save' in fields.keys():
                logger.info('Button pressed in form "general"->"save"')
                active_app_name = fields.get('active_app', '')
                self._update_active_app(active_app_name)
            elif 'update' in fields.keys():
                logger.info('Button pressed in form "general"->"update"')
                widget.update()     
            else:
                logger.warning('Should not happen in form "general"!')
        else:
            fields = _read_post_query()
            app_ids = self._get_app_ids()
            if (any([True for id in app_ids if (id in self.path)])):     
                app_id = self.path.replace('/', '')           
                logger.info(F"Valid app found: {app_id}")
                self._update_app(app_id, fields)
            else:
                logger.warning('Invalid App Requested!')
        
        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))
            
    def do_GET(self):
        logger.info(F"Website Root is requested")
        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))
         
def create_server(ip_address="0.0.0.0", port=8000):
    handler = WeatherImageRequestHandler
    server_address = (ip_address, port)
    httpd = HTTPServer(server_address, handler)
    logger.info(F"Open Browser with: http://192.168.2.133:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    create_server()
