from read_image import create_snapshot, image_processing
from send_image import send_image
from threading import Timer, Lock

class Periodic(object):
    """
    A periodic task running in threading.Timers
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()
        

def fetch_and_upload_image():
    image_path = "weather.png" # is used to temporary store a image
        
    create_snapshot("manuel-jasch.de/weather-forecast/weather.php", 600, 800, image_path)
    
    image_processing(image_path)
    
    send_image(image_path)
    
    
def main():
    seconds = 60*60 # call script every 1h
    
    fetch_and_upload_image() # call on start up
    per = Periodic(seconds, fetch_and_upload_image, autostart=True)
    #per.start()
    #per.stop() 
    
    
if __name__ == '__main__':
    main()