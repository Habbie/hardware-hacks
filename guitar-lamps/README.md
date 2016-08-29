# guitar-lamps
The plan is to control mood lighting using a Guitar Hero controller. Am halfway.

Some credit to http://whatacowpi.blogspot.com/2012/07/connecting-wii-nunchuck-to-raspberry-pi.html

If you're going to imitate this, I recommend keeping http://wiibrew.org/wiki/Wiimote/Extension_Controllers handy - I only found it after figuring out a lot of things by hand.

## Guitar-side deployment

Edit IPs in init.lua and pins in guitar.lua, then ship *.lua to an ESP8266 (I tested with NodeMCU and Wemos D1) using luatool. Make sure your firmware has I2C. My pins (1 and 2) are actually labeled D1 and D2 on the NodeMCU and the Wemos.

Some images of the physical setup in [this imgur album](http://imgur.com/a/AoNG4).

## Lamp-side deployment

I don't actually own led strips or mood lights or whatever. I run `nc -u -l 0 2000 | ~/guitar-stdin-xterm` on the IP configured in init.lua and let it colour my screen (https://youtu.be/wZGP3cPInG0).

Files:
* guitar.lua - mildly inspired by https://github.com/samularity/nodemcu_lua/blob/master/nunchuk.lua but adapted to use the non-encrypted protocol based on the whatacowpi blogpost
* init.lua - bootup script, taken from luatool + 4 new lines
* nunchuck.c - hacked up version from blogpost above
* guitar.c - guitar client for linux (tested on raspbian)
* guitar-stdin.c - parse 6 byte guitar messages from stdin
* guitar-stdin-xterm.c - as above but color the whole screen based on the input