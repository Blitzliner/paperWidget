# paperWidget
An electronic e-paper display which is used to display widgets e.g. weather forecast.

## Setup the Hardware
### Wiring
Raspberry Pi -> E-Ink Display

Pin 1 3.3V	--> 6 - VCC
GND		--> 5 - GND
Pin 10 GPIO 15	--> 4 - DOUT
Pin 8 GPIO 14	--> 3 - DIN
Pin 7 GPIO 4	--> 2 - WAKE_UP
Pin 3 GPIO 2	--> 1 - RST

### Preparation
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

## Execute Script on Startup
How to configure main script to be executed on startup?
1. sudo raspi-config
   Boot Options->Desktop/CLI select Console Autologin
2. sudo nano /etc/profile
   add:
   sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py 

or for endless scripts run in the background
sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py &

# Headless Pi preparation
The Pi shall be used without GUI. On Startup the main.py script shall be executed. For easier access SSH is set up.
## Static Ip Address
Connect to wifi first!
Get the Gateway Address of wifi and ethernet:
    route -ne
Get the domain name server:
    cat /etc/resolv.conf
Edit dhcpcd.conf file:
    sudo nano /etc/dhcpcd.conf
Add the following lines:
    interface eth0
    static ip_address=10.0.0.100
    static routers=10.0.0.1
    static domain_name_servers=75.75.75.75 75.75.76.76 2001:558:feed::1 2001:558:feed::2

    interface wlan0
    static ip_address=10.0.0.99
    static routers=10.0.0.1
    static domain_name_servers=75.75.75.75 75.75.76.76 2001:558:feed::1 2001:558:feed::2
    

## SSH
### Activate on Pi:
0. Set master passwort of pi
1. sudo nano /etc/ssh/sshd_config 
"PermitRootLogin" change to:
PermitRootLogin yes
2. STRG + O
   STRG + X
3. sudo service ssh restart

### Activate on Windows
1. Settings->Optional Feature Install "OpenSSH Client"
2. CMD: ssh pi@192.168.2.133
3. CMD: type "yes" and type in password

# Reduction of Power Consumption
1. deactivate  HDMI
deactivate:
    /usr/bin/tvservice -o
activate
    /usr/bin/tvservice -p
2. disable LEDs
Add following lines to /boot/config.txt:
    dtparam=act_led_trigger=none
    dtparam=act_led_activelow=off
    dtparam=pwr_led_trigger=none
    dtparam=pwr_led_activelow=off
3. deactivate Bluetooth 
Add following line to /boot/config.txt:
    dtoverlay=disable-bt


# TODOs
- Add Sever for the settings
- Apply everything on the Pi Zero
- Support of 2Bit Images
-
