# E-Paper Widgets
An electronic e-paper display which is used to display widgets for example the weather forecast.
For the Project following things are used:
- E-Ink Display from Waveshare (800x600, 4.3inch, Serial Interface)
- Raspberry Pi Zero W (W stands for Wifi)

# Installation
## Hardware
Connect the Raspberry Pi with the E-Ink Display. The pinout is the same for pi zero and pi 2 and pi 3.
- Pin 1 3.3V	--> 6 - VCC
- GND		--> 5 - GND
- Pin 10 GPIO 15	--> 4 - DOUT
- Pin 8 GPIO 14	--> 3 - DIN
- Pin 7 GPIO 4	--> 2 - WAKE_UP
- Pin 3 GPIO 2	--> 1 - RST

## Software
### Headless Pi
The Pi shall be used without GUI. On Startup the main.py script shall be executed. For easier access SSH is set up.
1. Install OS: Pi Lite is installed with Raspberry Pi Imager
2. Create a new File on the sd boot root "wpa_supplicant.conf" with the following content:
```
country=DE

network={
    ssid="YOUR_NETWORK_NAME"
    psk="YOUR_PASSWORD"
    key_mgmt=WPA-PSK
}
```
3. Create an empty file with the name "ssh" under the sd boot root.
4. Enable auto login on boot by ```sudo raspi-config``` and select "Console auto-login for CLI".  Use "pi" as username and "raspberry" for the password. Hint: English keyboard is active. For using german keyboard layout you have to enter "raspberrz" as password.
Check wpa_supplicant.conf file if it is not working. For apply changes execute ```wpa_cli -i wlan0 reconfigure```.
5. Change default password with ```passwd```

Troubleshooting:
Adapter is missing:
Add adaptor to interfaces ```sudo nano /etc/network/interfaces``` by adding the following lines:
```
auto wlan0
iface wlan0 inet manual
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```
After applying the changes reboot the pi.

### SSH
Activate on Pi:
0. Please set master passwort of pi first.
1. Enable ssh by opening ```sudo nano /etc/ssh/sshd_config``` change
```PermitRootLogin``` to: ```PermitRootLogin yes```
2. Restart SSH with ```sudo service ssh restart```

Activate on Windows:
1. Install SSH feature: 
   Settings->Optional Feature Install "OpenSSH Client"
2. Go to terminal and enter ```ssh pi@192.168.2.133``` and confirm with ```yes``` followed by the password

### Preparation
1. Clone this repository to the pi desktop with ```git clone https://github.com/Blitzliner/paperWidget.git```.
If git is not pre installed intall it with ```sudo apt update && sudo apt install git```
2. You may have to install other librarys:
- wkhtmltopdf: ```sudo apt install wkhtmltopdf```
- backfill for PIL: ```sudo apt-get install libopenjp2-7 && sudo apt install libtiff5``` (Maybe not neccessary)
- backfill for Numpy: ```sudo apt-get install libf77blas.so.3```

3. Edit /boot/cmdline.txt with ```sudo nano /boot/cmdline.txt``` and delete the parameter "console=serial0, 115200" from the line

4. Edit /boot/config.txt with ```sudo nano /boot/config.txt``` and add the line "enable_uart=1". Reboot after that.
   
5. Install python libs
   ```
   sudo apt-get update
   sudp apt install libpython-dev python3-rpi.gpio
   sudo apt install python3-pip
   pip3 install -U pyserial
   sudo apt install python-pil
   sudo apt install python3-numpy
   ```
6. Test the scripts from /home/pi/paperWidget/common/*.py. Every script has a main function to test basic functionality.

Troubleshooting:
On the pi zero w the standard uart is mapped to the bluetooth interface. You can switch it by adding at the end of /boot/config.txt: dtoverlay=pi3-miniuart-bt. Read more about here https://www.raspberrypi.org/documentation/configuration/uart.md
   
## Execute Script on Startup
How to configure server script to be executed on startup?
1. Open the rasberry configuration with ```sudo raspi-config``` 
   In the GUI go to Boot Options->Desktop/CLI select Console Autologin
2. Open crontab configuration by ```crontab -e```
3. Add new line for running server.py and widget.py on startup and execute widget every start of an hour.
   ```
   @reboot python3 /home/pi/Desktop/paperWidget/common/server.py &
   @reboot python3 /home/pi/Desktop/paperWidget/common/widget.py &
   0 * * * *  python3 /home/pi/Desktop/paperWidget/common/widget.py
   ```
   
# Advanced
## Static Ip Address
Connect to wifi first!
1. Get the Gateway Address of wifi and ethernet with ```route -ne```
2. Get the domain name server bye ```cat /etc/resolv.conf```
3. Edit dhcpcd.conf file with ```sudo nano /etc/dhcpcd.conf```

Add the following lines:
```
    interface eth0
    static ip_address=10.0.0.100
    static routers=10.0.0.1
    static domain_name_servers=75.75.75.75 75.75.76.76 2001:558:feed::1 2001:558:feed::2

    interface wlan0
    static ip_address=10.0.0.99
    static routers=10.0.0.1
    static domain_name_servers=75.75.75.75 75.75.76.76 2001:558:feed::1 2001:558:feed::2
``` 

## Reduction of Power Consumption
1. Deactivate HDMI
   deactivate by ```/usr/bin/tvservice -o```
   activate by ```/usr/bin/tvservice -p```
2. Disable LEDs
   Edit /boot/config.txt with ```sudo nano /boot/config.txt``` and add following lines:
    ```
    dtparam=act_led_trigger=none
    dtparam=act_led_activelow=off
    dtparam=pwr_led_trigger=none
    dtparam=pwr_led_activelow=off
    ```
3. Deactivate Bluetooth 
   Edit /boot/config.txt with ```sudo nano /boot/config.txt``` and add ```dtoverlay=disable-bt```

# TODOs
Hardware
- [x] Use of Pi Zero instead of Pi 3
- [ ] Power savings
- [ ] Build a frame for it

Feature
- [ ] Support of 2Bit Images -> Update would take too long
An update of Image with 40000 lines takes 66 seconds.
- [ ] Preview of Image in grayscale

Refactor
- [x] Create extra script for app configuration -> config.py get_available_apps(), get_general(app_id), get_parameter(app_id), get_setting(app_id, setting_name)

Done
- [x] Support for Uploading images but still problems with too many lines
- [x] Add Sever for the settings
- [x] Save last execution and check for new one instead of threading (save to config.cfg last_executed: timestamp)
- [x] support of one other example app e.g. joke of the day
