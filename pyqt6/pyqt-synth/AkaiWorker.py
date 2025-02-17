"""
"""

import mido
from pyqtgraph.Qt import (
        QtWidgets,
        QtCore,)


class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.
    467
    progress
    int progress complete,from 0-100
    """
    master_volume = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()


class AkaiWorker(QtCore.QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handle worker thread setup, signals
    and wrap-up.
    """

    def __init__(self, midi_port_name="MIDI Mix:MIDI Mix MIDI 1 20:0"):
        super().__init__()
        self.signals = WorkerSignals()
        self.input_port = mido.open_input(midi_port_name)
        self.output_port = mido.open_output(midi_port_name)

    def close_ports(self):
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()

    @QtCore.pyqtSlot()
    def run(self):
        # total_n = 1000
        try:
            while True:
                # Check for any pending messages
                for message in self.input_port.iter_pending():
                    print("Pending:", message)
                    # Process the pending message if needed

                # Process incoming messages
                for message in self.input_port:
                    # Process the received message

                    if message.is_cc():
                        # print('Control change message received')

                        if message.control == 62:
                            mvolume = message.value
                            print("Master Control", message.control,
                                  "value", message.value)
                            self.signals.master_volume.emit(mvolume)
                        # self.process_control_change_message(message)
                        # self.callback(self.mixer)
        except KeyboardInterrupt:
            self.close_ports()
            self.signals.finished.emit()  # Done
            print("Exiting...")
        except Exception as e:
            print(f"Error processing messages: {e}")
