Raspberry Pi -> E-Ink Display

Pin 1 3.3V	--> 6 - VCC
GND		--> 5 - GND
Pin 10 GPIO 15	--> 4 - DOUT
Pin 8 GPIO 14	--> 3 - DIN
Pin 7 GPIO 4	--> 2 - WAKE_UP
Pin 3 GPIO 2	--> 1 - RST




Config Pi Hardware

1. Edit /boot/cmdline.txt and delete the parameter 
console=serial0, 115200 from the line
sudo nano /boot/cmdline.txt

2. Edit /boot/config.txt and add the line enable_urat=1
sudo nano /boot/config.txt

3. reboot

4. install python libs
sudo apt-get update
sudp apt-get install libpython-dev python3-rpi.gpio
sudo apt-get install python3-pip
pip3 install -U pyserial

git clone https://github.com/jarret/raspi-uart-waveshare.git

5. test a basic exmaple from the git
python3 test_basic.py



Configure main script to be executed on startup
1. sudo raspi-config
   Boot Options->Desktop/CLI select Console Autologin
2. sudo nano /etc/profile
   add:
   sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py 

or for endless scripts run in the background
sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py &
