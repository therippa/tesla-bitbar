# Tesla BitBar Plugin

A simple plugin that lets you view the battery/charging status and control the HVAC from your OSX menubar.

![](https://i.imgur.com/Vj5o80V.png)

Supports multiple vehicles

![](https://i.imgur.com/XfkzAra.png)

## Instructions
1. Install the latest version of [BitBar](https://github.com/matryer/bitbar/releases/latest).
2. Open a terminal and run `sudo pip install keyring`
3. Copy [tesla.30m.py](tesla.30m.py) to your BitBar plugins folder.
4. Start BitBar, or if already running, click the BitBar menu and choose Preferences -> Refresh all.


### Note for multiple vehicles
If you haven't named your vehicle, it will show up in the menu named as the last six of your VIN number.  To give your vehicle a human-readable name, edit the VEHICLES object in the script file to match you VIN and chosen name.  Alternatively, in the car at the top of your 17" screen, tap the big Tesla 'T'. That will pull up your VIN and, in the upper right of the window, you will see "Name Your Vehicle"
