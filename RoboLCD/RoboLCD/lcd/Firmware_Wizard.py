from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from .. import roboprinter
from functools import partial
from kivy.logger import Logger
from kivy.clock import Clock
from pconsole import pconsole
import thread
from connection_popup import Error_Popup
import sys
import os
import tempfile
import traceback
import shutil
import subprocess
from scrollbox import ScrollBox, Scroll_Box_Even

if sys.platform == "win32":
    USB_DIR = 'C:\\Users\\mauro\\AppData\\Roaming\\OctoPrint\\uploads\\USB'
    FILES_DIR = 'C:\\Users\\mauro\\AppData\\Roaming\\OctoPrint\\uploads'
else:
    USB_DIR = '/home/pi/.octoprint/uploads/USB'
    FILES_DIR = '/home/pi/.octoprint/uploads'

class Firmware_Wizard(FloatLayout):
    
    def __init__(self,robosm, back_destination):
        super(Firmware_Wizard, self).__init__()
        self.sm = robosm
        files = self._find_hex_in_usb()
        if files:
            #continue to the hex select screen
            back_destination = self.sm.current
            name = roboprinter.lang.pack['Firmware_Wizard']['Select_Firmware']
            buttons = []
            for file in files:
                temp_button = Hex_Button(file, files[file], self.generate_confirmation)
                buttons.append(temp_button)
            layout = Scroll_Box_Even(buttons)

            self.sm._generate_backbutton_screen(name = name, title = name, back_destination=back_destination, content=layout)
        

            

        else:
            #show warning saying that we cannot detect a hex file on the USB
            ep = Error_Popup(roboprinter.lang.pack['Firmware_Wizard']['Hex_Error_Title'], roboprinter.lang.pack['Firmware_Wizard']['Hex_Error_Body'],callback=partial(roboprinter.robosm.go_back_to_main, tab='printer_status_tab'))
            ep.open()




    def generate_confirmation(self,name, path):
        flash = roboprinter.printer_instance.flash_usb
        screen_name = "hex_confirmation"
        title = roboprinter.lang.pack['Firmware_Wizard']['Confirm_Hex']
        back_destination = self.sm.current
        layout = Hex_Confirmation_Screen(name, path, flash)
        self.sm._generate_backbutton_screen(name = screen_name, title = title, back_destination=back_destination, content=layout)

    def _find_hex_in_usb(self):
        hex_files = {}
        for r, d, files in os.walk(USB_DIR):
            for f in files:
                if (f.endswith('.hex') ) and not f.startswith('._') :
                    path = r + '/' + f
                    hex_files[f] = path
                else:
                    continue
        return hex_files

class Hex_Button(Button):
    button_text = StringProperty("Error")
    hex_name = StringProperty("ERROR")
    path = StringProperty("Error")
    button_function = ObjectProperty(None)
    def __init__(self,hexname, path, function):
        super(Hex_Button, self).__init__()
        self.hex_name = hexname
        self.path = path
        self.button_function = function
        self.button_text = self.hex_name


class Hex_Confirmation_Screen(GridLayout):
    hex_name = StringProperty("Error")
    path = StringProperty("Error")
    button_function = ObjectProperty(None)

    def __init__(self, name, path, function):
        super(Hex_Confirmation_Screen, self).__init__()
        self.hex_name = name
        self.path = path
        self.button_function = function
