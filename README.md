# E-Paper Widgets
An electronic e-paper display which is used to display widgets for example the weather forecast.

## Setup the Hardware
### Wiring
Raspberry Pi -> E-Ink Display

- Pin 1 3.3V	--> 6 - VCC
- GND		--> 5 - GND
- Pin 10 GPIO 15	--> 4 - DOUT
- Pin 8 GPIO 14	--> 3 - DIN
- Pin 7 GPIO 4	--> 2 - WAKE_UP
- Pin 3 GPIO 2	--> 1 - RST

### Preparation
1. Edit /boot/cmdline.txt with ```sudo nano /boot/config.txt``` and delete the parameter 
console=serial0, 115200 from the line

2. Edit /boot/config.txt with ```sudo nano /boot/config.txt``` and add the line enable_uart=1
   
3. Rreboot

4. Install python libs
   ```
   sudo apt-get update
   sudp apt-get install libpython-dev python3-rpi.gpio
   sudo apt-get install python3-pip
   pip3 install -U pyserial

   git clone https://github.com/jarret/raspi-uart-waveshare.git
   ```
5. Test a basic exmaple from the git with ```python3 test_basic.py```
   
## Execute Script on Startup
How to configure main script to be executed on startup?
1. Open the rasberry configuration with ```sudo raspi-config``` 
   In the GUI go to Boot Options->Desktop/CLI select Console Autologin
2. Execute script on start up
   open ```sudo nano /etc/profile``` and add the following line:
   ```sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py```
   or for endless scripts run in the background
   ```sudo python3 /home/pi/Desktop/paperWidget/e_pape/main.py &```

# Headless Pi preparation
The Pi shall be used without GUI. On Startup the main.py script shall be executed. For easier access SSH is set up.
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

## SSH
### Activate on Pi:
Please set master passwort of pi first.
1. Enable ssh by opening ```sudo nano /etc/ssh/sshd_config``` change
```PermitRootLogin``` to: ```PermitRootLogin yes```
2. Restart SSH with ```sudo service ssh restart```

### Activate on Windows
1. Install SSH feature: 
   Settings->Optional Feature Install "OpenSSH Client"
2. Go to terminal and enter ```ssh pi@192.168.2.133``` and confirm with ```yes``` followed by the password

# Reduction of Power Consumption
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
- [ ] Use of Pi Zero instead of Pi 3
- [ ] Add Sever for the settings
- [ ] Support of 2Bit Images
- [ ] Support for Uploading images
- [ ] Power savings
