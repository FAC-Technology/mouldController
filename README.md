Python environment for monitoring of Eurotherm Nanodac controllers using their native website. Use IP_ADDRESSES.txt to list the controllers that should be online.  

Tkinter is used for the interface whilst each DAC is represented as a class. 

INSTALLATION
1. Install git on the computer. Can be found here https://git-scm.com/download/win. 
 Use this to clone this repository to a suitable location on the computer. (Recommend C:/Moulds). 
2. Install python 3.8 on the computer. Can be found here https://www.python.org/downloads/release/python-380/
  You probably want Windows x86-64 executable installer if on a fairly modern windows laptop.  
2. Clone this repository
3. Copy paste this into a powershell window opened in the repository directory

python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt

5. Script is run using
  python main.py


EXPLANATION OF CURE CYCLE DETECTION ALGORITHM:
The temperature is examined from the present time backwards in 3minute bins. If a 3 minute bin 
within the temperature range of postcuring is detected, the time is added to the end of an empty list. 
If the temperature leaves the window, the time is inserted at the start of 
the list. If the list is an odd length, the temperature at the point of examination
must be within the cure boundaries. If it is even, the temperature history must've
left the region. 

This gives us the following possibilities:

1. The list of times is of zero length - the panel never reached the postcure temp.
2. The list of items is of length 1 - the time history does not see the temperature
permanently leave the temperature boundary. Unlikely? 
3. The list is of even length, and the first and last times are greater than the
required cure time - the panel reached the right window, but may have left in between.
This is noted in the results, when 'Monitor dac_X' is pressed. 
4. The list is of even length but does not span enough time - the 
algorithm searches until the beginnning of the time history. Tries again
from beginning for the cure.