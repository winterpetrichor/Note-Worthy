# Note-Worthy
## Description
GUI developed in Python to assist in developing sight reading for musicians. Code pitches (heh) a note and listens for that frequency. 

Correct notes spawn new notes. 

Pitched notes and "heard" notes are displayed on screen using matplotlib. 

Time and success stats are tracked and displayed in a chart.

Multithreading hacked together to make all this possible and allow pausing, etc.

## Some more details
This is a "repo" that I worked on locally for a while before starting on GitHub. 

It was created after doing a few intro/intermediate level courses and generally having an interest in creating a piece of software that does roughly what this does.

The implementation is not the best, and bits of it are hacked together from some code I don't fully understand, but managed to put to use in a way that seems to work. 

There are some notes in the code comments for planned future improvements, but I haven't modified this code in over a year.

The code is rough and generally uncommented. I may return to this repo in the future to refine it as I develop my skills. 

However, it's a working piece of code that I think, with my level of experience, should be part of my portfolio at this stage.

## How to run
If you have all the dependencies and Python 3.9, you should just be able to download the .py file and the .xlsx file and give it a go.

Otherwise, you can download the entire dist folder and run the .exe

### Dependencies
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex
import sys
import time
import random
import numpy as np
import pyaudio
import pyqtgraph as pg
import pandas as pd
from types import SimpleNamespace
import os.path
from os import path
import csv