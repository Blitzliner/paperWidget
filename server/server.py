
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
from PIL import Image
from urllib.parse import urlparse, parse_qs


class WeatherImageRequestHandler(BaseHTTPRequestHandler):#http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200) # 200 Ok: everything is okay
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_Head(self):
        self._set_headers()

    def do_GET(self):
        if '/weather' in self.path:
            self._set_headers()
            query = parse_qs(urlparse(self.path).query)
            city = query.get('city', ['Koblenz'])[0]
            bins = query.get('bins', [20])[0]
            html = "<html><head></head><body>city: {}</br>bins: {}</h1></body></html>".format(city, bins)
            self.wfile.write(bytes(html, "utf8"))


# install snapshot tool for websites:
# sudo apt install wkhtmltopdf
# test in console with the following
# wkhtmltoimage --height 1200 --width 800 google.com out.png
# hint all fonts need to be converted to base64 and shall be available for true_font and woff
# transfonter.org for help converting it
def create_snapshot(address, height, width, out_path, city='Koblenz', bins=17):
    address = "{}?city={}&entries={}".format(address, city, bins)
    program = "wkhtmltoimage"
    args = [program, "--height", str(height), "--width", str(width), address, out_path]
    subprocess.call(args)
    
def create_snapshot_local(address, height, width, out_path):
    program = "wkhtmltoimage"
    args = [program, "--height", str(height), "--width", str(width), address, out_path]
    subprocess.call(args)

def image_processing(image_path):
     img = Image.open(image_path).convert('L').resize((800, 600))
     img = img.point(lambda x: 0 if x<128 else 255)
     img.save(image_path)
    
def create_server(port=8000):
    handler = WeatherImageRequestHandler
#    server_address = ("localhost", port)
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, handler)
    print("open webbrowser with:\nlocalhost:{}/weather?city=Koblenz&bins=16".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def main():
    image_path = "weather.png"
    #create_snapshot("manuel-jasch.de/weather-forecast/weather.php", 600, 800, image_path)
    create_snapshot_local("../widgets/weather-forecast/weather_js.html", 600, 800, image_path)
    image_processing(image_path)
    create_server()

if __name__ == '__main__':
    main()
