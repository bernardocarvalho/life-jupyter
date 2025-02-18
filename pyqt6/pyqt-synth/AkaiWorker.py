"""
"""

import mido
from pyqtgraph.Qt import (
        QtCore,)

NUM_HARMONICS = 8
HARM_VOLUMES = [16, 20, 24, 28, 46, 50, 54, 58,]

# Notes
BUTTON_NOTES = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27]

MUTE_NOTES = [1, 4, 7, 10, 13, 16, 19, 22,]
REC_ARM_NOTES = [3, 6, 9, 12, 15, 18, 21, 24,]
SOLO_NOTE = 27


class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.
    467
    progress
    int progress complete,from 0-100
    """
    masterVolume = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    harmonicUpdate = QtCore.pyqtSignal(dict)


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
        # self.harmonics = []
        self.harmonics = [{'order': 0, 'amplitude': 0, 'recArm': False,
                           'phase': 0.0, 'mute': False}]
        for order in range(1, NUM_HARMONICS):
            self.harmonics.append(
                    {'order': order, 'amplitude': 0, 'recArm': False,
                     'phase': 0.0, 'mute': True})
            # self.harm.append(Harmonic())
        self.reset_lights()
        self.keep_running = True

    def close_ports(self):
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()

    def send_light_state(self, note_number, ledOn=False):
        """Send light updates based on the toggle states."""
        if ledOn:
            vel = 127
        else:
            vel = 0
        msg = mido.Message('note_on', note=note_number, velocity=vel)
        # print("Led msg", msg)
        self.output_port.send(msg)

    def reset_lights(self):
        for nt in BUTTON_NOTES:
            # pass
            self.send_light_state(nt, False)
        self.send_light_state(1, True)

    def update_harmonic_control(self, harm, button, value):
        if (button == 0):
            pass
        elif (button == 2):
            self.harmonics[harm]['phase'] = value
            # print(self.harmonics[harm])
            self.signals.harmonicUpdate.emit(self.harmonics[harm])
        elif (button == 3):
            self.harmonics[harm]['amplitude'] = value
            print(self.harmonics[harm])
            self.signals.harmonicUpdate.emit(self.harmonics[harm])

    def update_harmonic_mute(self, harm):
        if self.harmonics[harm]['mute']:
            self.harmonics[harm]['mute'] = False
            vel = 0
        else:
            self.harmonics[harm]['mute'] = True
            vel = 127

        note_number = MUTE_NOTES[harm]
        msg = mido.Message('note_on', note=note_number, velocity=vel)
        print("Led msg", msg)
        self.output_port.send(msg)

    def update_harmonic_rec_arm(self, harm):
        if self.harmonics[harm]['recArm']:
            self.harmonics[harm]['recArm'] = False
            vel = 0
        else:
            self.harmonics[harm]['recArm'] = True
            vel = 127
        note_number = REC_ARM_NOTES[harm]
        msg = mido.Message('note_on', note=note_number, velocity=vel)
        # print("Led msg", msg)
        self.output_port.send(msg)

    def process_message(self, msg):

        if msg.is_cc():
            # print('Control change message received')

            if msg.control == 62:
                mvolume = msg.value
                self.signals.masterVolume.emit(mvolume)
            else:
                for h, cbase in enumerate(HARM_VOLUMES):
                    for btn in range(4):
                        if msg.control == cbase + btn:
                            print(f"Control H:{h} CB:{cbase} BT:{btn} Val:{msg.value}")
                            # print(self.harmonics[h])
                            self.update_harmonic_control(h, btn, msg.value)

        elif msg.type == 'note_on':
            harm = next((i for i, x in enumerate(MUTE_NOTES)
                         if x == msg.note), None)
            if harm is not None:
                self.update_harmonic_mute(harm)
            harm = next((i for i, x in enumerate(REC_ARM_NOTES)
                         if x == msg.note), None)
            if harm is not None:
                self.update_harmonic_rec_arm(harm)

        elif msg.type in ['note_on', 'note_off']:
            print("Type", msg.type,
                  "Note", msg.note)

    @QtCore.pyqtSlot()
    def run(self):
        # total_n = 1000
        try:
            while self.keep_running:
                # Check for any pending messages
                for message in self.input_port.iter_pending():
                    print("Pending:", message)
                    # Process the pending message if needed

                # Process incoming messages
                for message in self.input_port:
                    self.process_message(message)
                    # Process the received message

                        # self.callback(self.mixer)
        except KeyboardInterrupt:
            self.close_ports()
            self.signals.finished.emit()  # Done
            print("Exiting...")
        except Exception as e:
            print(f"Error processing messages: {e}")

        self.signals.finished.emit()  # Done
