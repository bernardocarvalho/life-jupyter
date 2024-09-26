#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6 App to Synthesize Composite Fourier Serier
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
from scipy.io.wavfile import write
# from scipy import signal
from Signal import Signal, Sine, Square, Sawtooth, Chirp
from datetime import datetime

from PyQt6.QtCore import (
        QSize,
        QTimer,
        Qt,
        )

from PyQt6.QtWidgets import (
    # QButtonGroup,
    QWidget,
    QApplication,
    QDial,
    QLineEdit, QTableView,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QDialog,
    # QDialogButtonBox, QCheckBox, QComboBox, QGroupBox, QMessageBox,
    QPushButton,
    QSlider,
    # QSpinBox, QRadioButton, QTabWidget,
    QLabel,
)

UPDATE_PERIOD = 1000  # Sample Period in millisec
NUM_HARMONICS = 7
INITIAL_VOL = np.array([10, 5, 0, 0, 0, 1, 0])
AUDIO_RATE = 44100
freq = 440
length = 0.02  # in sec
num_samples = int(AUDIO_RATE * length)

# create time values
# generate y values for signal
# save to wave file
# write("sine.wav", AUDIO_RATE, y)


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
    parser.add_argument('-u', '--simUl',
                        action='store_true', help='Simulation Mode')
    args = vars(parser.parse_args())
    return args


class HarmonicControl(QWidget):
    def __init__(self, parent=None, order=5):
        super().__init__(parent)
        # super().__init__(*args, **kwargs)
        # print(f'order = {order}')

        layout = QVBoxLayout()
        lblOrd = QLabel(f'Ordem = {order}')
        layout.addWidget(lblOrd)
        # self.slider = QSlider(Qt.Orientation.Vertical, self)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(0, 0, 20, 50)
        self.slider.setMinimum(0)
        self.slider.setMaximum(180)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(90)
        layout.addWidget(self.slider)
        layout.addWidget(QLabel('Phase'))

        self.dialAmp = QDial()
        self.dialAmp.setGeometry(0, 0, 30, 30)
        self.dialAmp.setMinimum(0)
        self.dialAmp.setMaximum(10)
        self.dialAmp.setValue(0)
        self.dialAmp.valueChanged.connect(self.sliderMoved)
        layout.addWidget(self.dialAmp)
        layout.addWidget(QLabel('Ampl'))
        self.setLayout(layout)

    def sliderMoved(self):
        print("Dial value = %i" % (self.dialAmp.value()))


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

    def textbox_text_changed(self):
        self.echo_label.setText(self.textbox.text())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fourier Shyntesizer")
        args = parseCommandLine()  # Return command line arguments
        self.simul = args['simUl']
        self.val = 5.0

        container = QWidget()
        layoutMain = QVBoxLayout()
        layoutHarmonics = QHBoxLayout()
        layoutMain.addLayout(layoutHarmonics)
        lblTr = QLabel('Temperature RED')
        lblTr.setStyleSheet("color: red")
        lblTr.setFixedHeight(80)
        # layoutMain.addWidget(lblTr, 0, 0)
        self.harmonics = []
        for i in range(NUM_HARMONICS):
            h = HarmonicControl(order=(i+1))
            h.dialAmp.setValue(INITIAL_VOL[i])
            self.harmonics.append(h)
            layoutHarmonics.addWidget(h)
        # layoutMain.addWidget(slider, 0, 0)
        #lblTb = QLabel('Temperature BLUE')
        #lblTb.setStyleSheet("color: blue")
        # layoutMain.addWidget(lblTb, 0, 1)
        # layoutMain.addWidget(self.Tredlabel, 1, 0)
        # self.Tbluelabel = QLabel('11.0')
        # layoutMain.addWidget(self.Tbluelabel, 1, 1)
        plotWdg = pg.PlotWidget(title="Plot")
        layoutMain.addWidget(plotWdg, stretch=2)  # , 2, 0, 1, 2)
        # samples = args['samples']  # Number of sample to store
        # create time values
        self.time = np.linspace(0, length, num_samples,
                                dtype=np.float32)
# generate y values for signal
        self.y = np.sin(2 * np.pi * freq * self.time)
        self.y += 0.5 * np.sin(2 * np.pi * freq * 3 * self.time)
        # self.SoundCurve = plotWdg.plot(self.time, self.y, pen='red')

        sig0 = Sine(440, length=2)
        sig1 = Sine(2 * 440, length=2)
        sig2 = sig0.__add__(sig1)
        self.sig = sig2  # Sine(440, length=2)
        self.SoundCurve = plotWdg.plot(self.sig.ts[:1024],
                                       self.sig.ys[:1024], pen='red')
        # plotT.setYRange(10, 105)
        # plotT.plot(self.TredArray)  # pen=({'color: red', 'width: 1'}), name="ch{1}")

        layoutButtons = QHBoxLayout()
        saveBtn = QPushButton('Save Data')
        saveBtn.clicked.connect(self.save_data)
        layoutButtons.addWidget(saveBtn)  # , 3, 0)
        playBtn = QPushButton('Play Sound')
        playBtn.clicked.connect(self.pydub_play)
        layoutButtons.addWidget(playBtn)  # , 3, 0)
        saveWav = QPushButton('Save Wav')
        saveWav.clicked.connect(self.save_wav)
        layoutButtons.addWidget(saveWav)  # , 3, 0)
        layoutMain.addLayout(layoutButtons)
        # self.echotext_widget = EchoText()
        # layoutMain.addWidget(self.echotext_widget)

        container.setLayout(layoutMain)
        self.setMinimumSize(QSize(1200, 700))
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_panels)
        self.timer.start(UPDATE_PERIOD)  # Sample Period in millisec

    def pydub_play(self):
        self.sig.play()

    def save_data(self):
        T_mat = np.array([self.TredArray, self.TblueArray])

        filename = f"Temperature_log_{datetime.now():%Y-%m-%d_%H-%m-%d}.csv"
        np.savetxt(filename, T_mat.T, delimiter=",")

    def save_wav(self):
        self.sig.to_wav('som.wav')

    def update_panels(self):
        # xdata.append((float(data[0]) - timeStart )/1000.0 )
        print(self.harmonics[0].dialAmp.value())
        try:
            # self.SoundCurve.setData(self.time, self.y)
            self.SoundCurve.setData(self.sig.ts[:1024],
                                    self.sig.ys[:1024])

        except KeyboardInterrupt:
            sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# vim: syntax=python ts=4 sw=4 sts=4 sr et
