# binary-scope

While working on guitar-lamps, somebody asked 'now, can you also control the lighting while the guitar is actually being used to play Guitar Hero'. I realised that my options would be to bridge the I2C, or to sniff the I2C. This directory is the result of my experiments in sniffing.

Much credit to @mgottschlag on #raspberrypi who pointed out to me that the Raspberry Pi's SPI support, if you don't connect the clock anywhere, is 'a generic high-frequency GPIO input accelerator' - in other words, you can pretty much stream the state of a specific GPIO pin from it at configurable speed.

Most/all of this document assumes you've hooked the I2Cs SDA line to https://pinout.xyz/pinout/pin21_gpio9.

## dumping from `/dev/spidev*`

Enable SPI via `raspi-config`.

Dumping directly from `/dev/spidev*` works well:
```
dd if=/dev/spidev0.0 bs=4096 | pv > /dev/null
 368KiB 0:00:06 [60.9KiB/s] [...
```

From measuring the output rate, it appears we are sampling at roughly 486kHz - close enough to the 488 kHz mentioned at https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md. This is fine for sniffing between 8266 and the guitar as I measured that at around 45kHz, but my understanding is that an actual Wiimote will transfer at 400kHz, which means we need to sample at at least 800kHz to reliably detect all edges.

And given that SDA is silent (high) between transactions, `hexdump -C` is useful:
```
$ hexdump -C /dev/spidev0.0
00000000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
00030ff0  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff f0  |................|
00031000  00 03 ff 00 00 00 00 ff  ff ff ff ff ff ff ff ff  |................|
00031010  ff ff ff ff ff ff ff ff  c0 00 00 00 00 00 00 00  |................|
00031020  00 00 00 3f ff ff ff ff  ff ff ff ff ff ff ff ff  |...?............|
00031030  e0 0f ff ff ff ff ff ff  ff ff ff ff ff f8 00 00  |................|
...
```

The edges are easy to spot here as well - notice `03 ff 00` on the fourth line for example, 11 sampled high bits, reflecting the shortest 'high' period in this transaction, which is where I got the 486/11 = 45 kHz measurement for this pair of devices. (Sampling at twice the rate, near 1mHz, indeed stretches these runs to 20-23 bits).

I ran `dd if=/dev/spidev0.0 bs=4096 of=sda-1transaction-1` and did one transaction on the SDA line of the I2C bus I'm sniffing (between ESP8266 and the guitar). I made 3 of these files. The edge count is consistent, suggesting that nothing is getting missed or dropped.
```
$ for d in sda-1transaction-* ; do python ./toedges.py < $d ; echo ; done
10101010101010101010101010101010101010101010101010101010101010101010101010101010101010101
10101010101010101010101010101010101010101010101010101010101010101010101010101010101010101
10101010101010101010101010101010101010101010101010101010101010101010101010101010101010101
```

So, reading directly from the device file is fine if we're content with a fixed ~500kHz sample rate.

## per-message reading

Disable SPI via `raspi-config`.

Based on https://github.com/raspberrypi/linux/blob/master/Documentation/spi/spidev_test.c (modified version in this directory) I made an SPI dumper that behaves just like the dd calls above, but is more configurable:
```
$ ./spidev_test -s 500000 -D /dev/spidev0.0 | hexdump -C
00000000  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
000281a0  ff ff f8 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000281b0  00 00 00 00 00 00 00 00  00 00 03 ff f0 03 ff 80  |................|
```

Using this, we can try various sample rates and see what happens. 

```
$ ./spidev_test -s 500000 -D /dev/spidev0.0 | pv > /dev/null
 184KiB 0:00:03 [60.9KiB/s] [
```

Output rate is consistent with direct `/dev` reads. Doubling the speed in steps leads to a double output rate, up to 64MHz. At 128 (125) MHz I only see about a 50% increase compared to 64MHz. Given that we need around 800 kHz, this is absolutely fine.

## edge triggered GPIO+epoll

Disable SPI via `raspi-config` and run `gpio export 9 in; gpio edge 9 both`.

epolltest waits for GPIO state to change, then outputs a whole byte (`0x00` or `0xff`).
```
$ ./epolltest   | hexdump -C
00000000  ff 00 ff 00 ff 00 ff ff  00 00 00 ff ff 00 00 00  |................|
```

The same transaction as before only yields nine edges now. It appears the epoll-based interface responds way too slowly for us! In fact, we can tell just from the longer-than-one runs that after the edge trigger, we read the same value as before. This means that between the interrupt and our read, the value has changed from under us at least once. In other words, we are missing a lot of events here.

According to posters in https://www.raspberrypi.org/forums/viewtopic.php?f=33&t=84696, there appears to be a 100 microsecond delay. At 45 kHz, our events can be as short as 20 microseconds - down to 2 microseconds at 400 kHz. So, this is not going to work.

## actively polling `/sys/class/gpio/gpioX/value`

```
$ ./pollingtest | pv > /dev/null
1.79MiB 0:00:15 [ 125KiB/s]
```

So that looks like a rough MHz. However, when evaluating the output with `toedges.py` I am missing between 50% and 75% of edges. I have not investigated why this is.

## other options
* mmap SPI via `/dev/mem` ([apparently this can be done](http://raspberrypi.stackexchange.com/a/2044)) - I'm not sure how useful this is for me compared to my `spidev_test.c` or reading from `/dev/spidev*` (which can also be set to a higher frequency)
* mmap GPIO via `/dev/mem` or `/dev/gpiomem` - but I fear this might be as unreliable as reading from `/sys/...`. Did not verify this.

## further ideas
* for one of the feasible sniffing methods, add support to https://sigrok.org/wiki/Supported_hardware so I don't have to write my own I2C decoder