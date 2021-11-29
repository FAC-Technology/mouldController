Python environment for monitoring of Eurotherm Nanodac controllers using their native website. Use IP_ADDRESSES.txt to list the controllers that should be online.  

Tkinter is used for the interface whilst each DAC is represented as a class. 

INSTALLATION
0. Install git on the computer. Can be found here https://git-scm.com/download/win
1. Install python 3.8 on the computer. Can be found here https://www.python.org/downloads/release/python-380/
  You probably want Windows x86-64 executable installer if on a fairly modern windows laptop.  
2. Clone this repositoryy
3. Copy paste this into a powershell window opened in the repository directory

python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt

5. Script is run using
  python main.py
