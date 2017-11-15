# Tesla BitBar Plugin

A simple plugin that lets you view the battery/charging status and control the HVAC and locks from your OSX menubar.

![](https://i.imgur.com/4LNLTVm.png)

Supports multiple vehicles (please ignore the outdated menu options)

![](https://i.imgur.com/XfkzAra.png)

## Instructions
1. Install the latest version of [BitBar](https://github.com/matryer/bitbar/releases/latest).
2. Open a terminal and run `sudo pip install keyring`
3. Copy [tesla.30m.py](tesla.30m.py) to your BitBar plugins folder, and run `chmod +x tesla.30m.py` from your terminal in that folder.
4. Start BitBar, or if already running, click the BitBar menu and choose Preferences -> Refresh all.

## After about 45 days, it won't work anymore...why?
Your token expired.  Open a terminal and run `keyring del tesla-bitbar access-token`, then refresh the plugin.  It will ask you to log in again, creating a new token.

### Note for multiple vehicles
If you haven't named your vehicle, it will show up in the menu named as the last six of your VIN number.  To fix this, in the car at the top of your 17" screen, tap the big Tesla 'T'. That will pull up your VIN and, in the upper right of the window, you will see "Name Your Vehicle"
