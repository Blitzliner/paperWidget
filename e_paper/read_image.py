import subprocess
from PIL import Image


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
    
def image_processing(image_path):
     img = Image.open(image_path).convert('L').resize((800, 600))
     img = img.point(lambda x: 0 if x<128 else 255)
     img.save(image_path)
   
# test function
def main():
    image_path = "weather.png"
    create_snapshot("manuel-jasch.de/weather-forecast/weather.php", 600, 800, image_path)
    image_processing(image_path)

if __name__ == '__main__':
    main()

