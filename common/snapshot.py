import subprocess
from PIL import Image
import logging
import configparser
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s (%(name)s): %(message)s')
logger = logging.getLogger(__name__)

def _image_processing(image_path):
    logger.info("Convert Image to grayscale")
    img = Image.open(image_path).convert('L').resize((800, 600))
    img = img.point(lambda x: 0 if x<128 else 255)
    img.save(image_path)
    
# install snapshot tool for websites:
# sudo apt install wkhtmltopdf
# test in console with the following
# wkhtmltoimage --height 1200 --width 800 google.com out.png
# hint all fonts need to be converted to base64 and shall be available for true_font and woff
# transfonter.org for help converting it
def snap(address, parameter, height, width, out_path, processing=True):
    params = ""
    for key, value in parameter.items():
        params += "&{}={}".format(key, value)
    if len(params) > 0:
        address += "?" + params[1:]
    logger.info("Address: " + address)
    
    logger.info("Create snapshot with wkhtmltoimage")
    program = "wkhtmltoimage"
    args = [program, "--height", str(height), "--width", str(width), address, out_path]
    try: 
        subprocess.call(args)
    except FileNotFoundError:
        logger.error("wkhtmltoimage not found")
        shutil.copyfile('fallback.jpg', out_path)
    
    if processing:
        _image_processing(out_path)
        

if __name__ == '__main__':
    image_path = "snapshot.png"
    cfg = configparser.ConfigParser()
    cfg.read('../apps/weather-forecast/config.cfg')
    snap("manuel-jasch.de/weather-forecast/weather.php", cfg['parameter'], 600, 800, image_path)

