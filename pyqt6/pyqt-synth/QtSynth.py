#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 App to Synthesize and composite Fourier Series type Sound
author:  B. Carvalho / IPFN-IST
email: bernardo.carvalho@tecnico.ulisboa.pt
https://medium.com/@noahhradek/sound-synthesis-in-python-4e60614010da
https://gist.github.com/nhrade/7cfcdf9e00602e52f516f90315b5d26e
"""
import sys
import argparse
# import serial
import pyqtgraph as pg
import numpy as np
# from scipy.io.wavfile import write
# from scipy import signal
from Signal import Signal, Sine, Square, Sawtooth, Chirp
from datetime import datetime
# from pyqtgraph import Qt
from pyqtgraph.Qt import (
        QtWidgets,
        QtCore,)


UPDATE_PERIOD = 1000  # Update signal / plot Period, in millisec
NUM_HARMONICS = 9
# INITIAL_VOL = np.array([50, 0, 20, 0, 0, 1, 0, 0, 0])
FULL_VOL = 100
INITIAL_VOL = np.array([100, 0, 11, 0, 4, 0, 2, 0, 1])
AUDIO_RATE = 44100
# length = 0.02  # in sec
# num_samples = int(AUDIO_RATE * length)

# AlignmentFlag
af = QtCore.Qt.AlignmentFlag


def parseCommandLine():
    """Use argparse to parse the command line for specifying
    a device to use.
    parser.add_argument("-f", "--file", type=str,
        help="A path to a .qml file to be the source.",
        required=True)
    parser.add_argument('-d', '--device', type=str,
                        help='Serial device to use', default=DEVICE)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--samples', type=int,
                        help='Number of samples to Show/Store', default=120)
    parser.add_argument('-f', '--frequency', type=int,
                        help='Main signal frequency in Hz', default=440)
    parser.add_argument('-l', '--length', type=int,
                        help='Signal Lenght in s', default=2)
    parser.add_argument('-u', '--simUl',
                        action='store_true', help='Simulation Mode')
    args = vars(parser.parse_args())
    return args


class HarmonicControl(QtWidgets.QWidget):
    def __init__(self, parent=None, order=5):
        super().__init__(parent)
        # super().__init__(*args, **kwargs)
        # print(f'order = {order}')
        self.order = order
        self.phase = 0
        layout = QtWidgets.QVBoxLayout()
        lblOrd = QtWidgets.QLabel(f'Ordem = {order}')
        lblOrd.setAlignment(af.AlignHCenter)

        layout.addWidget(lblOrd)
        separatorLine = QtWidgets.QFrame()
        separatorLine.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        layout.addWidget(separatorLine)
        # self.slider = QSlider(Qt.Orientation.Vertical, self)
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self)
        slider.setGeometry(0, 0, 20, 50)
        slider.setMinimum(-1)
        slider.setMaximum(1)
        slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        # slider.setTickInterval(90)
        # slider.setSingleStep(90)
        self.sliderPhase = slider
        layout.addWidget(self.sliderPhase)
        self.lblPhase = QtWidgets.QLabel('Phase')
        self.lblPhase.setAlignment(af.AlignHCenter)
        layout.addWidget(self.lblPhase)
        self.sliderPhase.valueChanged.connect(self.phaseMoved)

        dial = QtWidgets.QDial()
        dial.setGeometry(0, 0, 30, 30)
        dial.setMinimum(-90)
        dial.setMaximum(90)
        dial.setValue(0)
        dial.setNotchesVisible(True)
        self.dialPhase = dial
        layout.addWidget(self.dialPhase)
        self.dialPhase.valueChanged.connect(self.phaseMoved)
        separatorLine = QtWidgets.QFrame()
        separatorLine.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        layout.addWidget(separatorLine)
        # layout.addSeparator()

        dial = QtWidgets.QDial()
        dial.setGeometry(0, 0, 30, 30)
        dial.setMinimum(0)
        dial.setMaximum(100)
        # self.dialAmp.setValue(0)
        dial.setNotchesVisible(True)
        self.dialAmp = dial
        self.dialAmp.valueChanged.connect(self.dialMoved)
        layout.addWidget(self.dialAmp)
        self.lblAmp = QtWidgets.QLabel("Amp:")
        layout.addWidget(self.lblAmp)
        self.setLayout(layout)

    def phaseMoved(self):
        self.phase = self.dialPhase.value() + 90 * self.sliderPhase.value()
        self.lblPhase.setText(f"Phase: {self.phase}")
        # print(f"Phase: {self.phase}")

    def dialMoved(self):
        self.lblAmp.setText(f"Amp: {self.dialAmp.value()}")

    def sliderMoved(self):
        print("Dial value = %i" % (self.dialAmp.value()))
        self.lblAmp.setText(f"Amp: {self.dialAmp.value()}")

    def textbox_text_changed(self):
        self.echo_label.setText(self.textbox.text())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IST - LFE Fourier Shyntesizer")
        args = parseCommandLine()  # Return command line arguments
        self.freq = args['frequency']
        self.length = args['length']
        # self.val = 5.0

        container = QtWidgets.QWidget()
        layoutMain = QtWidgets.QVBoxLayout()
        layoutHarmonics = QtWidgets.QHBoxLayout()
        layoutMain.addLayout(layoutHarmonics)
        lblTr = QtWidgets.QLabel('Temperature RED')
        lblTr.setStyleSheet("color: red")
        lblTr.setFixedHeight(80)
        # layoutMain.addWidget(lblTr, 0, 0)
        self.harmonics = []
        for i in range(NUM_HARMONICS):
            h = HarmonicControl(order=(i+1))
            h.dialAmp.setValue(INITIAL_VOL[i])
            self.harmonics.append(h)
            layoutHarmonics.addWidget(h)
        # lblTb.setStyleSheet("color: blue")
        # layoutMain.addWidget(self.Tredlabel, 1, 0)
        # self.Tbluelabel = QLabel('11.0')
        # layoutMain.addWidget(self.Tbluelabel, 1, 1)
        plotWdg = pg.PlotWidget(title="Plot")
        layoutMain.addWidget(plotWdg, stretch=2)  # , 2, 0, 1, 2)
        # samples = args['samples']  # Number of sample to store
        # create time values
        # self.time = np.linspace(0, length, num_samples,
        #                        dtype=np.float32)
# generate y values for signal
        # self.y = np.sin(2 * np.pi * freq * self.time)
        # self.y += 0.5 * np.sin(2 * np.pi * freq * 3 * self.time)
        # self.SoundCurve = plotWdg.plot(self.time, self.y, pen='red')

        self.SoundCurve = plotWdg.plot(pen='r')
        # self.SoundCurve = plotWdg.plot(self.sig.ts[:1024],
        #                               self.sig.ys[:1024], pen='rd')
        # plotT.setYRange(10, 105)
        # plotT.plot(self.TredArray)  # pen=({'color: red', 'width: 1'}), name="ch{1}")

        layoutButtons = QtWidgets.QHBoxLayout()
        resetBtn = QtWidgets.QPushButton('Reset Sinus')
        resetBtn.clicked.connect(self.reset_sinus)
        layoutButtons.addWidget(resetBtn)  # , 3, 0)
        saveBtn = QtWidgets.QPushButton('Save Data')
        saveBtn.clicked.connect(self.save_data)
        layoutButtons.addWidget(saveBtn)  # , 3, 0)
        playBtn = QtWidgets.QPushButton('Play Sound')
        playBtn.clicked.connect(self.pydub_play)
        layoutButtons.addWidget(playBtn)  # , 3, 0)
        saveWav = QtWidgets.QPushButton('Save Wav')
        saveWav.clicked.connect(self.save_wav)
        layoutButtons.addWidget(saveWav)  # , 3, 0)
        layoutMain.addLayout(layoutButtons)
        # self.echotext_widget = EchoText()
        # layoutMain.addWidget(self.echotext_widget)

        container.setLayout(layoutMain)
        self.setMinimumSize(QtCore.QSize(1200, 700))
        self.setCentralWidget(container)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_panels)
        self.timer.start(UPDATE_PERIOD)  # Sample Period in millisec

    def pydub_play(self):
        self.sig.play()

    def save_data(self):
        T_mat = np.array([self.sig.ts, self.sig.ys])

        filename = f"Sound_{datetime.now():%Y-%m-%d_%H-%m-%d}.csv"
        np.savetxt(filename, T_mat.T, delimiter=",")

    def save_wav(self):
        self.sig.to_wav('som.wav')

    def reset_sinus(self):
        self.harmonics[0].dialAmp.setValue(FULL_VOL)
        for i in range(1, NUM_HARMONICS):
            self.harmonics[i].dialAmp.setValue(0)
        for i in range(0, NUM_HARMONICS):
            self.harmonics[i].dialPhase.setValue(0)
            self.harmonics[i].sliderPhase.setValue(0)
            self.harmonics[i].phaseMoved()

    def update_panels(self):
        # xdata.append((float(data[0]) - timeStart )/1000.0 )
        try:
            # print(f"Order 1:Amp {self.harmonics[0].dialAmp.value()}", end='')

            a = self.harmonics[0].dialAmp.value()
            ph = self.harmonics[0].phase
            sig = Sine(self.freq, amp=a, phase=ph, length=self.length)
            # print("Order:Amp  ", end='')
            for i in range(1, NUM_HARMONICS):
                a = self.harmonics[i].dialAmp.value()
                ph = self.harmonics[i].phase
                # ph = self.harmonics[i].dialPhase.value()
                n = self.harmonics[i].order
                # print(f" {i+1}:{a},", end='')

                siga = Sine(n * self.freq, a, ph, self.length)
                sig = sig.__add__(siga)
            # print("")
            self.sig = sig
            # self.SoundCurve.setData(self.time, self.y)
            self.SoundCurve.setData(self.sig.ts[:1024],
                                    self.sig.ys[:1024])

        except KeyboardInterrupt:
            print("Interrupt")
            sys.exit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

"""
class EchoText(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.textbox = QLineEdit()
        self.echo_label = QLabel('')

        self.textbox.textChanged.connect(self.textbox_text_changed)

        self.layout.addWidget(self.textbox, 0, 0)
        self.layout.addWidget(self.echo_label, 1, 0)
"""
# vim: syntax=python ts=4 sw=4 sts=4 sr et
