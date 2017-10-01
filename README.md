# Tesla BitBar Plugin

A simple plugin that lets you view the battery/charging status and control the HVAC from your OSX menubar.

![](https://i.imgur.com/Vj5o80V.png)

Supports multiple vehicles

![](https://i.imgur.com/XfkzAra.png)

## Instructions
1. Install the latest version of [BitBar](https://github.com/matryer/bitbar/releases/latest).
2. Open a terminal and run `sudo pip install keyring`
3. After installation, run `keyring set tesla-bitbar youremail@email.com` using your tesla.com account email, and enter your password.
4. Copy [tesla.30m.py](tesla.30m.py) to your BitBar plugins folder.
5. Open tesla.30m.py in a text editor, and change the USERNAME variable to your tesla.com account email.
6. Start BitBar, or if already running, click the BitBar menu and choose Preferences -> Refresh all.


### Note for multiple vehicles
When running the plugin for the first time, your vehicle will show up in the menu named as the last six of your VIN number.  To give your vehicle a human-readable name, edit the VEHICLES object in the script file to match you VIN and chosen name.
