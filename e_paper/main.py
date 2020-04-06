from read_image import create_snapshot, image_processing
from send_image import send_image


def main():
    image_path = "weather.png"
    
    create_snapshot("manuel-jasch.de/weather-forecast/weather.php", 600, 800, image_path)
    
    image_processing(image_path)
    
    send_image(image_path)
    
    
    
    
if __name__ == '__main__':
    main()