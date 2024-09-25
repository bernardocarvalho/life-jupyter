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
from scipy import signal
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

DEVICE = '/dev/ttyUSB0'
SAMPLE_PERIOD = 1000  # Sample Period in millisec

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
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', type=str,
                        help='Serial device to use', default=DEVICE)
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
        self.harmonic1 = HarmonicControl(order=1)
        layoutHarmonics.addWidget(self.harmonic1)
        self.harmonic2 = HarmonicControl(order=2)
        layoutHarmonics.addWidget(self.harmonic2)
        self.harmonic3 = HarmonicControl(order=3)
        layoutHarmonics.addWidget(self.harmonic3)
        self.harmonic4 = HarmonicControl(order=4)
        layoutHarmonics.addWidget(self.harmonic4)
        self.harmonic5 = HarmonicControl(order=5)
        layoutHarmonics.addWidget(self.harmonic5)
        self.harmonic6 = HarmonicControl(order=6)
        layoutHarmonics.addWidget(self.harmonic6)
        # layoutMain.addWidget(slider, 0, 0)
        lblTb = QLabel('Temperature BLUE')
        lblTb.setStyleSheet("color: blue")
        # layoutMain.addWidget(lblTb, 0, 1)
        self.Tredlabel = QLabel('10.0')
        # layoutMain.addWidget(self.Tredlabel, 1, 0)
        self.Tbluelabel = QLabel('11.0')
        # layoutMain.addWidget(self.Tbluelabel, 1, 1)
        plotWdg = pg.PlotWidget(title="Plot")
        layoutMain.addWidget(plotWdg, stretch=3)  # , 2, 0, 1, 2)
        # samples = args['samples']  # Number of sample to store
        # create time values
        self.time = np.linspace(0, length, num_samples,
                                dtype=np.float32)
# generate y values for signal
        self.y = np.sin(2 * np.pi * freq * self.time)
        self.y += 0.5 * np.sin(2 * np.pi * freq * 3 * self.time)
        self.SoundCurve = plotWdg.plot(self.time, self.y, pen='red')
        # plotT.setYRange(10, 105)
        # plotT.plot(self.TredArray)  # pen=({'color: red', 'width: 1'}), name="ch{1}")

        saveBtn = QPushButton('Save Data')
        saveBtn.clicked.connect(self.save_data)
        layoutMain.addWidget(saveBtn)  # , 3, 0)
        # self.echotext_widget = EchoText()
        # layoutMain.addWidget(self.echotext_widget)

        container.setLayout(layoutMain)
        self.setMinimumSize(QSize(1200, 700))
        self.setCentralWidget(container)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_panels)
        self.timer.start(SAMPLE_PERIOD)  # Sample Period in millisec

    def save_data(self):
        T_mat = np.array([self.TredArray, self.TblueArray])

        filename = f"Temperature_log_{datetime.now():%Y-%m-%d_%H-%m-%d}.csv"
        np.savetxt(filename, T_mat.T, delimiter=",")

    def update_panels(self):
        # xdata.append((float(data[0]) - timeStart )/1000.0 )
        print(self.harmonic1.dialAmp.value())
        try:
            self.SoundCurve.setData(self.time, self.y)

        except KeyboardInterrupt:
            sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# vim: syntax=python ts=4 sw=4 sts=4 sr et
