from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import configparser
import logging
import os
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
        logger.info("Create website from from template and config files")
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
                logger.info(F"set active app to {active_app}")
                app_options += F'                    <option value="{app_id}" selected>{app_name}</option>\n'
            else:
                app_options += F'                    <option value="{app_id}">{app_name}</option>\n'
                
            app_str += F'            <details>\n'
            app_str += F'                <summary>{app_name}</summary>\n'
            app_str += F'                <form action="{app_id}">\n'
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
            logger.info(F"update {key} in {config_file} with {value}")
            if cfg.has_option('general', key):
                cfg.set('general', key, value[0])
            elif cfg.has_option('parameter', key):
                cfg.set('parameter', key, value[0])
        
        with open(config_file, 'w') as file:
            cfg.write(file)      
            
    def do_POST(self):
        if '/upload' in self.path:
            logger.warning('Not yet supported')
        
        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))
            
    def do_GET(self):
        if '/general' in self.path:
            logger.info('submit form "general"')
            query = parse_qs(urlparse(self.path).query)
            active_app_name = query.get('active_app', [''])[0]
            self._update_active_app(active_app_name)
        else:
            app_ids = self._get_app_ids()
            if (any([True for id in app_ids if (id in self.path)])):                
                logger.info(F"Valid app id detected in path: \n{self.path}")
                app_id = self.path.split('?')[0][1:] # get string before ? and cut the / in front of the string
                logger.info(F"app id: {app_id}")
                query = parse_qs(urlparse(self.path).query)
                self._update_app(app_id, query)
                # trigger a update of main script # todo refactor
                widget.update()
                        
        self._set_headers()
        self.wfile.write(bytes(self._get_website(), "utf8"))
         
    
def create_server(ip_address="0.0.0.0", port=8000):
    handler = WeatherImageRequestHandler
    server_address = (ip_address, port)
    httpd = HTTPServer(server_address, handler)
    print("open webbrowser with:\n[IP_OF_YOUR_RASPBERRY_PI]:{}".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def main():
    create_server()

if __name__ == '__main__':
    main()
