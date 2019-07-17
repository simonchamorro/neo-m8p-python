# Ublox NEO-M8P-2 Python Library

![Ublox NEO M6 on Nano Pi NEO](https://a.lnwpic.com/56v2fw.png)

## How to use

- Connect the NEO M8P via the serial interface to your PC (in my case I'm using a serial to USB adapter)
- If you're not sure what the address of the serial port is or if you're not sure the M8P is getting a signal, download the [Arduino IDE](https://www.arduino.cc/en/main/software), click `Tools>Port` (it will show you serial ports and in my case bluetooth, but since I know it can't be bluetooth, that rules that out), then `Tools>Serial Monitor`. You should see several lines coming in every 2s, all starting with strings a la `$GLGSV` or `$GNRMC` or others. 
- Note whatever socket/device you selected under `Tools/Port` -> that's the `ADDRESS`
- Open the script in this repo under `scripts/01-test-gps.py`, change the variable `ADDRESS`.
- Run the script `scripts/01-test-gps.py`. The first signal might take a few seconds (<10s), but if you're outdoors and your GPS antenna has a direct connection to the sky, you should soon get a fix.

I think I read somewhere that the max time to get the first GPS fix is something around 30s (and consecutive ones around 2s). So if you're not getting a signal immediately, that might be due to that. 

 