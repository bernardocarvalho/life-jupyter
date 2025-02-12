#!/usr/bin/python3

"""
Control
Volume

16 20 24  28  46 50 54 58 
17    
18

N1 N4
N3 N6 
|| ||         ||       ||   ||
19            49       61   62


python3 MidiMasterator.py

Available MIDI Input Ports:
Midi Through:Midi Through Port-0 14:0
MIDI Mix:MIDI Mix MIDI 1 24:0
Midi Through:Midi Through Port-0 14:0
MIDI Mix:MIDI Mix MIDI 1 24:0

Available MIDI Output Ports:
Midi Through:Midi Through Port-0 14:0
MIDI Mix:MIDI Mix MIDI 1 24:0
Midi Through:Midi Through Port-0 14:0
MIDI Mix:MIDI Mix MIDI 1 24:0
None
None
Processing MIDI messages. Press Ctrl+C to exit.

Volume slider 1 (form left)
Received: control_change channel=0 control=19 value=0 time=0
Bank A Processing MIDI messages. Press Ctrl+C to exit.
Received: control_change channel=0 control=19 value=0 time=0
Sent control change: control_change channel=0 control=19 value=0 time=0
0 and 1 are within 10 integers of each other.
To Output control_change channel=1 control=19 value=0 time=0

Buttol left bottom

Received: note_on channel=0 note=3 velocity=127 time=0
Bank A Processing MIDI messages. Press Ctrl+C to exit.
Received: note_on channel=0 note=3 velocity=127 time=0
Sent note: note_on channel=1 note=3 velocity=127 time=0
Note 3 is now turned off.
Lightswitch for: 3
To Output note_on channel=1 note=3 velocity=127 time=0
Lightswitch for: 1
Lightswitch for: 2
Lightswitch for: 53
...
Lightswitch for: 50
Lightswitch for: 56
BYE
Received: note_off channel=0 note=3 velocity=127 time=0
Bank A Processing MIDI messages. Press Ctrl+C to exit.
Received: note_off channel=0 note=3 velocity=127 time=0
Sent note: note_off channel=1 note=3 velocity=127 time=0
To Output note_off channel=1 note=3 velocity=127 time=0
BYE


"""
import mido
# from MidiMasterator import print_available_midi_connections

# Notes
notes = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27]

# Control Changes
control_changes = [
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 30, 31, 46, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    60, 61, 127]
CONTROLS = [
        {'control': 16, 'harm': 0, 'row': 0, },
        {'control': 17, 'harm': 0, 'row': 1, },
        {'control': 18, 'harm': 0, 'row': 2, },
        {'control': 19, 'harm': 0, 'row': 3, },
        {'control': 20, 'harm': 1, 'row': 0, },
        {'control': 21, 'harm': 1, 'row': 1, },
        {'control': 22, 'harm': 1, 'row': 2, },
        {'control': 23, 'harm': 1, 'row': 3, },
        {'control': 24, 'harm': 2, 'row': 0, },
        {'control': 25, 'harm': 2, 'row': 1, },
        {'control': 26, 'harm': 2, 'row': 2, },
        {'control': 27, 'harm': 2, 'row': 3, },
        {'control': 28, 'harm': 3, 'row': 0, },
        {'control': 29, 'harm': 3, 'row': 1, },
        {'control': 30, 'harm': 3, 'row': 2, },
        {'control': 31, 'harm': 3, 'row': 3, },
        {'control': 46, 'harm': 4, 'row': 0, },
        {'control': 47, 'harm': 4, 'row': 1, },
        {'control': 48, 'harm': 4, 'row': 2, },
        {'control': 49, 'harm': 4, 'row': 3, },
        {'control': 50, 'harm': 5, 'row': 0, },
        {'control': 51, 'harm': 5, 'row': 1, },
        {'control': 52, 'harm': 5, 'row': 2, },
        {'control': 53, 'harm': 5, 'row': 3, },
        {'control': 54, 'harm': 6, 'row': 0, },
        {'control': 55, 'harm': 6, 'row': 1, },
        {'control': 56, 'harm': 6, 'row': 2, },
        {'control': 57, 'harm': 6, 'row': 3, },
        {'control': 58, 'harm': 7, 'row': 0, },
        {'control': 59, 'harm': 7, 'row': 1, },
        {'control': 60, 'harm': 7, 'row': 2, },
        {'control': 61, 'harm': 7, 'row': 3, },
        ]
LOG_VOL = [
        {'note': 3, 'harm': 0, },
        {'note': 6, 'harm': 1, },
        ]
# Shifted Notes
shifted_notes = [3, 6, 9, 12, 15, 18, 21, 24]

# Notes after shift
after_shift = [35, 38, 41, 44, 47, 50, 53, 56]

# Notes with no light
no_light = [25, 26, 27]

# Add shifted notes after offset to the notes list
notes.extend([note + 32 for note in shifted_notes])

def print_available_midi_connections():
    """
    Print out all available MIDI connections.
    """
    print("Available MIDI Input Ports:")
    for port in mido.get_input_names():
        print(port)

    print("\nAvailable MIDI Output Ports:")
    for port in mido.get_output_names():
        print(port)

class AkaiMidimix:
    def __init__(self, cback, midi_port_name="MIDI Mix:MIDI Mix MIDI 1 24:0"):
        # self.input_port_name = input_port_name
        # self.output_port_name = output_port_name
        # self.input_port = None
        self.input_port = mido.open_input(midi_port_name)
        self.output_port = mido.open_output(midi_port_name)
        # self.output_port = None

        self.callback = cback
        self.bank_A = None
        self.bank_B = None
        self.bank_C = None
        self.bank_D = None
        self.bankstate = 0
        self.note_27_state = False  # Attribute to track the state of note 27
        self.toggle_states = {
            1: False, 2: False, 3: False, 4: False,
            5: False, 6: False, 7: False, 8: False,
            9: False, 10: False, 11: False, 12: False,
            13: False, 14: False, 15: False, 16: False,
            17: False, 18: False, 19: False, 20: False,
            21: False, 22: False, 23: False, 24: False,
            35: False, 38: False, 41: False, 44: False,
            47: False, 53: False, 50: False, 56: False
        }  # Dictionary to store toggle states
        self.mixer = lambda: None  # Empty object
        self.mixer.master_volume = 0
        self.mixer.harmonics = [
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            {'amp': 0.0, 'log': False, 'phase': 0.0, 'phaseShit': False},
            ]
        self.clear_lights()

    def receive_from_bank_1(self, message):
        print("To Output", message)
        # Process the message as needed
        # self.output_port.send(message)

    def receive_from_bank_2(self, message):
        print("Lightswitch for:", message.note)
        # Process the message as needed
        # self.output_port.send(message)

    def close_ports(self):
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()

    def process_control_change_message(self, message):
        #   use a generator expression:
        if message.control == 62:
            print("Master Control", message.control,
                  "value", message.value)
            self.mixer.master_volume = message.value
        else:
            ctrl = next((cont for cont in CONTROLS
                        if cont["control"] == message.control), None)
            if ctrl is None:
                print("No CONTROL")
            else:
                print("CONTROL", ctrl)
                if ctrl['row'] == 2:
                    self.mixer.harmonics[ctrl['harm']]['phase'] = 90 + \
                            (message.value - 66) / 127.0 * 180
                elif ctrl['row'] == 3:
                    self.mixer.harmonics[ctrl['harm']]['amp'] = \
                            message.value / 127.0

    def process_note_message(self, note):
        """
        Process note MIDI messages.

        Args:
            message (mido.Message): The MIDI message.
        """
        nte = next((nt for nt in LOG_VOL
                    if nt["note"] == note), None)
        if nte is not None:
            logState = self.mixer.harmonics[nte['harm']]['log']
            logState = not logState
            self.mixer.harmonics[nte['harm']]['log'] = logState
            self.send_light_state(note, logState)


        # Send note messages to the output port
        if note not in [25, 26, 27]:
            # if message.note in shifted_notes and self.note_27_state:
            #    message.note = message.note + 32
            #    self.send_note_message(message)
            # else:
            #    self.send_note_message(message)
            self.toggle_note_state(note)

    def clear_lights(self):
        for nt in notes:
            self.send_light_state(nt, False)

    def send_light_state(self, note_number, ledOn=False):
        """Send light updates based on the toggle states."""
        if ledOn:
            vel = 127
        else:
            vel = 0
        msg = mido.Message('note_on', note=note_number, velocity=vel)
        print("Led msg", msg)
        self.output_port.send(msg)
        # self.input_port.send(msg)

    def toggle_note_state(self, note_number):
        """Toggle the state of the note with the given note number."""
        if note_number in self.toggle_states:
            self.toggle_states[note_number] = \
                    not self.toggle_states[note_number]
            state = self.toggle_states[note_number]
            if state:
                state_message = "turned"
            else:
                state_message = "turned off"
            self.send_light_state(note_number, state)

            # state_message = "turned" if self.toggle_states[note_number] else "turned off"
            print(f"Note {note_number} is now {state_message}.")
            # self.send_light_update(note_number)
        else:
            self.toggle_states[note_number] = True  # Default to True if note not found
            print(f"Note {note_number} is now turned on.")
            self.send_light_update(note_number)

    def process_messages(self):
        try:
            print("Processing MIDI messages. Press Ctrl+C to exit.")

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
                        self.process_control_change_message(message)
                        self.callback(self.mixer)


                    #if message.

                    if message.is_cc(7):
                        print('Volume changed to', message.value)
                    # if message.type in ['note_on', 'note_off'] and message.note in [25, 26]:
                    elif message.type == 'note_on':
                        self.process_note_message(message.note)

                    if message.type in ['note_on', 'note_off']:
                        print("Type", message.type,
                              "Note", message.note)
                        # pass
                    #    self.toggle_state(message.note, message.type)

                    elif self.bankstate == 0:
                        if message.type == 'control_change':
                            pass
                        print("Received:", message)
                            #print("Control Change:", message)
                            # self.process_control_change_message(message)
                        # self.bank_A.process_messages(message)
                    """
                    elif self.bankstate == 1:
                        self.bank_B.process_messages(message)
                    elif self.bankstate == 2:
                        self.bank_C.process_messages(message)
                    elif self.bankstate == 3:
                        self.bank_D.process_messages(message)
                    else:
                        # Send all other message types to the output port
                        pass
                    """

        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"Error processing messages: {e}")


def print_control(mixer):
    print(mixer)


if __name__ == "__main__":
    print_available_midi_connections()
    input_port_name = "MIDI Mix:MIDI Mix MIDI 1 20:0"
    # This should be the Output Port of your MIDI Mix

    
    try:
        midiAkai = AkaiMidimix(print_control, input_port_name)  # output_port_name)
    except OSError as e:
        print(f"Error: {e}")
        exit(-1)
        # return False
    # except OSError:
    #    print("'unknown port 'MID Mix:MIDI Mix MIDI 1 24:0'")
    #if midiAkai.open_ports():
    midiAkai.process_messages()

    print(midiAkai.mixer.harmonics)
    midiAkai.close_ports()




