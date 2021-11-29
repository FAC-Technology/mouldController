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
