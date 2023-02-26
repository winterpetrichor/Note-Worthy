###################################
# COMPILE COMMAND:
# pyinstaller --noconfirm --onedir --windowed --name "Random Notes" --paths "C:\Users\flips\AppData\Local\Programs\Python\Python39\Lib\site-packages\PyQt6\Qt6\bin" --hidden-import "PyQt6.sip" --hidden-import "PyQt6.QtPrintSupport" --add-data "C:\Users\flips\AppData\Local\Programs\Python\Python39\Lib\site-packages\PyQt6\Qt6\plugins\platforms;platforms/" "C:\Users\flips\Scripts\Random Notes\Releases\RandomNotes V0.45 - alpha 00.py"

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout
import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex

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

win=pg.GraphicsLayoutWidget()
win.resize(1024,800)
win.setWindowTitle("Note-Worthy - Statistics Display")
win.show()


plt = pg.plot()
# title for the plot window
plotwindowtitle = "Note-Worthy - Music Staff Display"
# setting window title to plot window
plt.setWindowTitle(plotwindowtitle)



class MyThread(QThread):
    print("MyThread")

    pause_listening=0
    pause_time_cumulative=0

##    def __init__(self):
##        pause_listening=pause_listening=0
##        super().__init__()
        

######################################################################
######################################################################
#1) get rid of excel file guit_freq.xlsx - try to make local to code and adjustable a=440
#2) add function to change a440 to whatever - may need text input (with data validation) and button to apply
#3) get windows to line up side by side or something neater Control above staff and both of those to the left of stats maybe
#4) best fit line
#5) add trailing second note
#6) add note durations

######################################################################
######################################################################
    
    note_out = pyqtSignal(dict)

    def run(self):
        global startcount, freq_count
        print("MyThread\run")
        
        #print(skip_out)
        df = pd.read_excel(r'guit_freq.xlsx')

        sel_freq1=(df.sample())
        
        sel_freq=sel_freq1['Freq'].item()
        sel_led=sel_freq1['Ledger'].item()
        sel_acc=sel_freq1['Acc'].item()
        sel_name=sel_freq1['Note_name'].item()
        if sel_acc=="fla":
            flat_sharp=-1
        if sel_acc=="nat":
            flat_sharp=0
        if sel_acc=="sha":
            flat_sharp=1
        sel_plot = [(sel_led)]
        
        NOTE_MIN = 37       # D2b
        NOTE_MAX = 77       # F5
        FSAMP = 22050       # Sampling frequency in Hz
        FRAME_SIZE = 2048   # How many samples per frame?
        FRAMES_PER_FFT = 16 # FFT takes average across how many frames?
        SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
        FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT
        def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
        def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
        def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)
        def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
        imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
        imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))
        buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
        num_frames = 0
        stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)
        print(type(stream))
        print(stream)
        stream.start_stream()
        fwindow = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))
        print('sampling at', FSAMP, 'Hz with max resolution of', FREQ_STEP, 'Hz')
        print()

        freq_count=0
        startcount=0

        time_pause_start=0
        time_pause_end=0
        
        pausestartset=0

        while True:
            
            print("MyThread\run\while")

            print("pause1 ",self.pause_listening)
            ####### add code for pausing timer (time between notes)
            if self.pause_listening==1:
                time_pause_start=time.time()
                pausestartset=1
                #print("time pause start",time_pause_start)
            if self.pause_listening==0 and pausestartset==1:
                pausestartset=0
                time_pause_end=time.time()
                #print("time pause end",time_pause_end)
                self.pause_time_cumulative = time_pause_end - time_pause_start + self.pause_time_cumulative
                print("time pause cumulative",self.pause_time_cumulative)
            
            while self.pause_listening==1:
                print("paused")
                time.sleep(0.2)
                continue
            else:          
                pass

            # Shift the buffer down and new data in
            buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
            buf[-FRAME_SIZE:] = np.frombuffer(stream.read(FRAME_SIZE), np.int16)
            # Run the FFT on the windowed buffer
            fft = np.fft.rfft(buf * fwindow)
            maxamp=round(max(abs(fft))/1000)
            
            freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

            if startcount>0:
                if freq > 710 or freq < 73 or maxamp < 1000:
                    continue
##                if maxamp < 1000:
##                    continue



            # Get note number and nearest note
            n = freq_to_number(freq)
            n0 = int(round(n))

            # Console output once we have a full buffer
            num_frames += 1

####################################################
            #TEMPORARY CODE TESTING
####################################################
            #freq=random.uniform(80,700)
            #print("freq = ",freq)
####################################################




            note_info1 = abs(df['Freq']-freq).idxmin()
            note_info=(df.loc[[note_info1]])
            note_freq=note_info['Freq'].item()
            note_led=note_info['Ledger'].item()
            note_name=note_info['Note_name'].item()
            note_info2 = (df.loc[(df['Freq']==note_freq)])
            print("note info 2 ",note_info2)

            if flat_sharp==1:
                note_info3=note_info2.loc[note_info2['Note_name'].str.contains("#")]
                if not note_info3.empty:
                    note_freq=note_info3['Freq'].item()
                    note_led=note_info3['Ledger'].item()
                    note_name=note_info3['Note_name'].item()
                    note_acc=note_info3['Acc'].item()
                    
            if flat_sharp==-1:
                note_info3=note_info2.loc[note_info2['Note_name'].str.contains("b")]
                if not note_info3.empty:
                    note_freq=note_info3['Freq'].item()
                    note_led=note_info3['Ledger'].item()
                    note_name=note_info3['Note_name'].item()
                    note_acc=note_info3['Acc'].item()
                    
            if flat_sharp==0:
                note_info3=note_info2.loc[~note_info2['Note_name'].str.contains("b|#")]
                if not note_info3.empty:
                    note_freq=note_info3['Freq'].item()
                    note_led=note_info3['Ledger'].item()
                    note_name=note_info3['Note_name'].item()
                    note_acc=note_info3['Acc'].item()
                    

            print("note name ",note_name)


            m_fl1=-100
            m_sh1=-100
            m_fl2=-100
            m_sh2=-100

            if flat_sharp==1:
                m_fl1=-100
                m_sh1=1


            if flat_sharp==-1:
                m_fl1=1
                m_sh1=-100


            if "#" in note_name:
                m_fl2=-100
                m_sh2=1


            if "b" in note_name:
                m_fl2=1
                m_sh2=-100

            

                

            sel_out=sel_led
            
            if startcount>0:
                freq_out=note_led
            else:
                freq_out=-100

            freq_out=note_led
            acc1_out=flat_sharp
            
            if (freq_out <= 400 or sel_out <=400):
                C3_out=400
            else:
                C3_out=-100

            if (freq_out <= 300 or sel_out <=300):
                A2_out=300
            else:
                A2_out=-100

            if (freq_out <= 200 or sel_out <=200):
                F2_out=200
            else:
                F2_out=-100

            if (freq_out >= 1000 or sel_out >=1000):
                A4_out=1000
            else:
                A4_out=-100
                
            if (freq_out >= 1100 or sel_out >=1100):
                C5_out=1100
            else:
                C5_out=-100

            if (freq_out >= 1200 or sel_out >=1200):
                E5_out=1200
            else:
                E5_out=-100


            
            if freq_count==1:                
                #time.sleep(1)
                sel_freq1=(df.sample())
            
                sel_freq=sel_freq1['Freq'].item()
                sel_led=sel_freq1['Ledger'].item()
                sel_acc=sel_freq1['Acc'].item()
                sel_name=sel_freq1['Note_name'].item()
                if sel_acc=="fla":
                    flat_sharp=-1
                if sel_acc=="nat":
                    flat_sharp=0
                if sel_acc=="sha":
                    flat_sharp=1
                sel_plot = [(sel_led)]
                sel_out=sel_led
                freq_count=0
                if note_freq == sel_freq:
                    startcount=1
                    freq_count=0
                    pass
                else:
                    continue
                
            if note_freq == sel_freq and freq_count==0:
                freq_count=1
                

            note_dict={}

            for variable in ["freq_out", "sel_out", "C3_out", "A2_out", "F2_out", "A4_out", "C5_out", "E5_out", "m_fl1", "m_sh1", "m_fl2", "m_sh2", "note_name", "sel_name", "note_freq", "sel_freq"]:
                note_dict[variable] = eval(variable)
            
            #time.sleep(0.3)
            self.note_out.emit(note_dict)
            startcount=1

            
                
            





class Window(QDialog):
    print("Window")
    def __init__(self):
        print("__init__")
        super().__init__()

        self.title = "Note-Worthy - Control Window"
        self.top = 200
        self.left = 500
        self.width = 300
        self.height = 120
        #self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QVBoxLayout()
        
        #main staff lines
        staff_E3 = [500,500]
        staff_G3 = [600,600]
        staff_B3 = [700,700]
        staff_D4 = [800,800]
        staff_F4 = [900,900]
        
        #lower staff lines
        self.staff_C3 = [-100,-100]
        self.staff_A2 = [-100,-100]
        self.staff_F2 = [-100,-100]

        #upper staff lines
        self.staff_A4 = [-100,-100]
        self.staff_C5 = [-100,-100]
        self.staff_E5 = [-100,-100]


        staff_horiz = [0, 1000]
        self.sel_horiz = [450]
        self.sel_acc_horiz = [400]
        note_horiz = [550]
        self.note_acc_horiz = [550]
        self.staff_ext_horiz = [350,650]

        self.x = [note_horiz[0]]
        self.y=[-100]

        plt.setXRange(0, 1000)
        plt.setYRange(0, 1400)
        plt.setBackground('ffffff')
        plt.setTitle(title=("Press the 'Start Listening' in the Control Window to start then play the BLUE notes!"))

        lineE3 = plt.plot(staff_horiz, staff_E3, pen=pg.mkPen('k', width=3))
        lineG3 = plt.plot(staff_horiz, staff_G3, pen=pg.mkPen('k', width=3))
        lineB3 = plt.plot(staff_horiz, staff_B3, pen=pg.mkPen('k', width=3))
        lineD4 = plt.plot(staff_horiz, staff_D4, pen=pg.mkPen('k', width=3))
        lineF4 = plt.plot(staff_horiz, staff_F4, pen=pg.mkPen('k', width=3))

        font=QtGui.QFont("Arial", 12, QtGui.QFont.Normal)
        font.setPixelSize(40)
        self.sh1 = pg.TextItem(text="#", color='b')
        self.sh1.setFont(font)
        self.fl1 = pg.TextItem(text="\u266D", color='b')
        self.fl1.setFont(font)
        self.sh2 = pg.TextItem(text="#", color='r')
        self.sh2.setFont(font)
        self.fl2 = pg.TextItem(text="\u266D", color='r')
        self.fl2.setFont(font)

        fontTC=QtGui.QFont("Arial", 12, QtGui.QFont.Normal) 
        fontTC.setPixelSize(190)
        tc = pg.TextItem(text="\U0001D11E", color='k')
        tc.setFont(fontTC)
        tc.setPos(50,1250)
        plt.addItem(tc)

        count=-1
        self.sel_plot=[-100]
        self.note_plotted = plt.plot(self.x, self.y, pen='r', width=6, symbol='o', symbolPen='r', symbolSize=20, symbolBrush=(255,0,0))
        self.sel_note_plotted = plt.plot(self.sel_horiz, self.sel_plot, pen='b', width=6, symbol='o', symbolPen='b', symbolSize=20, symbolBrush=(0,0,255))
        self.lineC3 = plt.plot(self.staff_ext_horiz, self.staff_C3, pen=pg.mkPen('k', width=3))
        self.lineA2 = plt.plot(self.staff_ext_horiz, self.staff_A2, pen=pg.mkPen('k', width=3))
        self.lineF2 = plt.plot(self.staff_ext_horiz, self.staff_F2, pen=pg.mkPen('k', width=3))
        self.lineA4 = plt.plot(self.staff_ext_horiz, self.staff_A4, pen=pg.mkPen('k', width=3))
        self.lineC5 = plt.plot(self.staff_ext_horiz, self.staff_C5, pen=pg.mkPen('k', width=3))
        self.lineE5 = plt.plot(self.staff_ext_horiz, self.staff_E5, pen=pg.mkPen('k', width=3))

        self.sh1.setPos(self.sel_acc_horiz[0]-20,-100*self.sel_plot[0]+90)
        plt.addItem(self.sh1)

        self.fl1.setPos(self.sel_acc_horiz[0]-30,-100*self.sel_plot[0]+110)
        plt.addItem(self.fl1)

        note_name=""
        
        self.sh2.setPos(self.note_acc_horiz[0]-70,-100*self.y[0]+90)
        plt.addItem(self.sh2)
        
        self.fl2.setPos(self.note_acc_horiz[0]-80,-100*self.y[0]+110)
        plt.addItem(self.fl2)

        plt.getPlotItem().hideAxis('left')
        plt.getPlotItem().hideAxis('bottom')


        if not path.exists('scorecard.csv'):
            #self.stat = pd.read_csv(r'C:\Users\flips\Scripts\Random Notes\scorecard.csv')

            #print(stat)

            self.grouped_stat = [0]
            self.mean_stat = [0]
            #self.mean_stat = self.mean_stat.reset_index()

            #print(mean_stat)


            self.note_name_stat_list = [0]
            self.timer_stat_list = [0]

            self.note_name_mean_list = [0]
            self.timer_mean_list = [0]

            self.p2axisdict = {0:0}

            #self.p1 = win.addPlot(title="Average time per note", y=self.timer_stat_list)
            self.p1=pg.GraphItem(title="Average time per note", x=range(len(self.timer_stat_list)) ,y=self.timer_stat_list)
            #self.p1.setLabel('left', "Time", units='s')
            #self.p1.setLabel('bottom', "Count")

            self.plot_item1=win.addPlot()
            self.plot_item1.addItem(self.p1)

            win.nextRow()


            self.plot_item=win.addPlot()
            self.plot_item.setAxisItems(self.p2axisdict)


            self.p2 = pg.BarGraphItem(x=range(len(self.timer_mean_list)), height=self.timer_mean_list, width=0.5)

            self.plot_item.addItem(self.p2)

            self.plot_item.getAxis('bottom').setTicks([self.p2axisdict.items()])

        else:
            self.stat = pd.read_csv(r'scorecard.csv')

            #print(stat)

            self.grouped_stat = self.stat.groupby('NoteName')
            self.mean_stat = self.grouped_stat.mean()
            self.mean_stat = self.mean_stat.reset_index()

            #print(mean_stat)


            self.note_name_stat_list = self.stat['NoteName'].tolist()
            self.timer_stat_list = self.stat['AvgTime'].tolist()

            self.note_name_mean_list = self.mean_stat['NoteName'].tolist()
            self.timer_mean_list = self.mean_stat['AvgTime'].tolist()

            self.p2axisdict = dict(enumerate(self.note_name_mean_list))

            #self.p1 = win.addPlot(title="Average time per note", y=self.timer_stat_list)
            self.p1=pg.GraphItem(title="Average time per note", x=range(len(self.timer_stat_list)) ,y=self.timer_stat_list)
            #self.p1.setLabel('left', "Time", units='s')
            #self.p1.setLabel('bottom', "Count")

            self.plot_item1=win.addPlot()
            self.plot_item1.addItem(self.p1)

            win.nextRow()


            self.plot_item=win.addPlot()
            self.plot_item.setAxisItems(self.p2axisdict)


            self.p2 = pg.BarGraphItem(x=range(len(self.timer_mean_list)), height=self.timer_mean_list, width=0.5)

            self.plot_item.addItem(self.p2)

            self.plot_item.getAxis('bottom').setTicks([self.p2axisdict.items()])

        
        
        self.buttonStart = QPushButton("Start Listening")
        self.buttonStart.clicked.connect(self.startListening)
        
        self.buttonSkip = QPushButton("Next Note (Skip)")
        self.buttonSkip.clicked.connect(self.skipNote)
        self.buttonSkip.setEnabled(False)
        
        self.buttonPause = QPushButton("Pause Listening")
        self.buttonPause.clicked.connect(self.pauseListening)
        #pause_listening=0
        
        self.buttonStop = QPushButton("End Program")
        self.buttonStop.clicked.connect(self.stopListening)
        
        self.buttonStart.setStyleSheet('background-color:#cfffab')
        self.buttonSkip.setStyleSheet('background-color:#a3e3ff')
        self.buttonPause.setStyleSheet('background-color:#f7e672')
        self.buttonStop.setStyleSheet('background-color:#ff8080')
        

        self.time_start=time.time()##move to after button click
        self.notecount=0
        
        vbox.addWidget(self.buttonStart)
        vbox.addWidget(self.buttonSkip)
        vbox.addWidget(self.buttonPause)
        vbox.addWidget(self.buttonStop)

        self.setLayout(vbox)
        self.show()

        
    def startListening(self):
        print("startListening")
        self.buttonStart.setEnabled(False)
        self.buttonSkip.setEnabled(True)
        self.thread = MyThread()
        self.thread.note_out.connect(self.setListenVal)
        self.thread.start()
        #plt.setTitle(title=(""))


    def setListenVal(self, note_out):
        print("setListenVal")
        print(note_out)
        
        n = SimpleNamespace(**note_out)
        
        self.y[0]=n.freq_out
        print("freq out",n.freq_out)
        print("sel out",n.sel_out)
        if n.note_freq==n.sel_freq:
            self.note_plotted.setData(self.x,self.y, symbolPen='g', symbolBrush=(0,255,0))
            self.sh2.setColor(color='g')
            self.fl2.setColor(color='g')
            self.notecount=self.notecount+1
            self.timer=round((time.time()-self.time_start-MyThread.pause_time_cumulative),2)
            self.avg=round(self.timer/self.notecount,2)
            notestr=(str(n.sel_name + " = " + n.note_name +" - "))
            timerstr=(str(self.timer))
            countstr=(str(self.notecount))
            avgstr=str(self.avg)
            record=str(notestr + countstr + " notes in " + timerstr + " seconds!\n That's " + avgstr + " seconds per note!")
            plt.setTitle(title=(record))
            if not path.exists('scorecard.csv'):
                with open('scorecard.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['SelName','NoteName','Count','Timer','AvgTime'])
                    writer.writerow([n.sel_name,n.note_name,countstr,timerstr,avgstr])
                    #writer.writerow('')
            else:
                with open('scorecard.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([n.sel_name,n.note_name,countstr,timerstr,avgstr])
                    #writer.writerow('')

            self.stat = pd.read_csv(r'scorecard.csv')

            #print(self.stat)

            self.grouped_stat = self.stat.groupby('NoteName')
            self.mean_stat = self.grouped_stat.mean()
            self.mean_stat = self.mean_stat.reset_index()

            #print(self.mean_stat)


            self.note_name_stat_list = self.stat['NoteName'].tolist()
            self.timer_stat_list = self.stat['AvgTime'].tolist()

            self.note_name_mean_list = self.mean_stat['NoteName'].tolist()
            self.timer_mean_list = self.mean_stat['AvgTime'].tolist()

            self.p2axisdict = dict(enumerate(self.note_name_mean_list))
            self.plot_item.getAxis('bottom').setTicks([self.p2axisdict.items()])

##            print(self.timer_stat_list)
##            print(self.timer_mean_list)
##            print(self.p2axisdict)

            self.p1.setData(title="Average time per note", x=range(len(self.timer_stat_list)) ,y=self.timer_stat_list)
            self.p2.setOpts(x=range(len(self.timer_mean_list)), height=self.timer_mean_list, width=0.5)

            
                
            #time.sleep(1)
        else:
            self.note_plotted.setData(self.x,self.y, symbolPen='r', symbolBrush=(255,0,0))
            self.sh2.setColor(color='r')
            self.fl2.setColor(color='r')

        self.sel_plot=[n.sel_out]
        self.sel_note_plotted.setData(self.sel_horiz,self.sel_plot)
        
        self.staff_C3=[n.C3_out,n.C3_out]
        self.lineC3.setData(self.staff_ext_horiz,self.staff_C3)
        
        self.staff_A2=[n.A2_out,n.A2_out]
        self.lineA2.setData(self.staff_ext_horiz,self.staff_A2)

        self.staff_F2=[n.F2_out,n.F2_out]
        self.lineF2.setData(self.staff_ext_horiz,self.staff_F2)

        self.staff_A4=[n.A4_out,n.A4_out]
        self.lineA4.setData(self.staff_ext_horiz,self.staff_A4)

        self.staff_C5=[n.C5_out,n.C5_out]
        self.lineC5.setData(self.staff_ext_horiz,self.staff_C5)

        self.staff_E5=[n.E5_out,n.E5_out]
        self.lineE5.setData(self.staff_ext_horiz,self.staff_E5)

        self.sh1.setPos(self.sel_acc_horiz[0]-20,n.m_sh1*self.sel_plot[0]+90)

        self.fl1.setPos(self.sel_acc_horiz[0]-30,n.m_fl1*self.sel_plot[0]+110)

        self.sh2.setPos(self.note_acc_horiz[0]-70,n.m_sh2*self.y[0]+90)

        self.fl2.setPos(self.note_acc_horiz[0]-80,n.m_fl2*self.y[0]+110)

        
    def skipNote(self):
        global startcount, freq_count
        startcount=0
        freq_count=1
        print("skipNote")




    def pauseListening(self):
        print("pauseListening")
        print("pause2 ",MyThread.pause_listening)
        if MyThread.pause_listening==0:
            self.buttonPause.setText("Resume Listening")
            self.buttonPause.setStyleSheet('background-color:#ecc2ff')
            self.buttonSkip.setEnabled(False)
            MyThread.pause_listening=1
        else:
            self.buttonPause.setText("Pause Listening")
            self.buttonPause.setStyleSheet('background-color:#f7e672')
            self.buttonSkip.setEnabled(True)
            MyThread.pause_listening=0
        #sys.exit()



    def stopListening(self):
        print("stopListening")
        sys.exit()

        

        

##        if n.freq_out==n.sel_out:
##            self.note_plotted.setColor(color='g')
##        else:
##            self.note_plotted.setColor(color='r')
        




App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())






















    
