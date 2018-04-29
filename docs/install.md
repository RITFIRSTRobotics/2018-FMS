# Field Management System Installation Process

1. Get a Raspberry Pi 3 (B or B+, B+ would be better), a wireless access point/router (a Netgear N300/WNDR2000 was used in 2018) and a microSD card

2. Install Raspbian Lite onto the microSD card, put the card into the Pi, put a file (`touch .ssh` on linux) on the boot partition and boot. Change the password (usually to `ritfirst`)

3. Make sure `git`, `python3`, `pip3`, `node` (needs to be >= v7, so at the time of writing, the apt package needs to be uninstalled as it's too old, see [this](https://deb.nodesource.com) page for how to install from source), and `npm` (`tmux` is also very nice to have).

4. Install pip packages (using `pip3`): `pyserial`, `flask`, `flask-cors`, `jsonpickle`, and `marshmallow` (not 100% sure this is everything).

5. Clone all the github repositories from Github, then go into the scoreboard repository.

6. Run `npm install` (this should install all the packages from the package.json file, but I've had to do it manually once or twice; this takes time on the Pi)

The Pi is now setup as an FMS!

To run a match with scoreboard:

1. `cd 2018-scoreboard` and `npm start` (runs the scoreboard, not necessary for testing)

2. cd `../2018-fms` and run `./bootstrap-fms.sh` (and `./bootstrap-debug.sh` in another tmux window), making sure that all the ASCs are plugged in

    i) use the `l x` command to blink the debugging LED on an ASC (where `x` is the number of the serial object in the list shown, `x = 2` on the Pi must be a system port because it hangs the program and is always there), then make a color selection from there

    ii) use the commands to start/stop a match (see `help` for a full list)
    
# Robot Installation Process

## Method 1 (the much easier one)

1. Find an existing robot's microSD card or the master microSD card, make an image of it, then write the image to your new microSD card.

2. `git pull` and `cd core; git pull; cd ..` if you want to get the latest code

3. Edit `.botsettings` if applicable (only effects gripper bot settings at the time of writing)

4. Run `python3 src/robot.py` to start the robot program

## Method 2 (please don't do this)

1. Get a Raspberry Pi Zero W and Picon Zero hat and a microSD card

2. Install Raspbian Lite onto the microSD card, put a file (`touch .ssh` on linux) and the wireless settings (for the FMS router) on the boot partition, put the card into the Pi, boot, and find the IP of the Pi in the router's settings screen. SSH into the Pi and change the password (usually `ritfirst`)

3. Install packages (this one I probably can't get right off the top of my head, again, please do Method 1): `python-smbus`, `python3-smbus`, `python-dev`, `python3-dev`, `i2c-tools`, and `git`

4. Add `dtparam=i2c1=on` and `dtparam=i2c_arm=on` (this is 100% not right, I remember having to google this, see a working robot for the correct settings) to the end of `/boot/config.txt` and reboot.

5. Run an i2c scan and see if you can see the Picon Zero (`i2cdetect -y 1`, it should come up as 22)

6. Clone the repository and run `python3 src/robot.py` (you could install the systemd script if you wanted to, but it's not tested at the time of writing).

# FAQ 

Q) If nothing has a static IP, then how is everything configured?
A) Things get assigned IPs in the router based on MAC address

Q) What if I am a linux user or don't want to put `arudev` on my PC?
A) You have three options: manually copy every file a directory with the same name as the .ino file, make a patch for Arduino IDE to allow for source files to be in subdirectories, or build a makefile to do everything for you.
