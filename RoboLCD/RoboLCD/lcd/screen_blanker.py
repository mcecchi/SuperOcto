import sys
import subprocess
import atexit
import logging
from kivy.core.window import Window
from kivy.clock import Clock

class Screen_Blanker():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.bl_event = None
        self.blanked = False
        self.bl_interval = 0
        self.bl_ctl = '/sys/devices/platform/rpi_backlight/backlight/rpi_backlight/bl_power'
        if sys.platform != "win32":
            subprocess.call('sudo chmod 666 ' + self.bl_ctl, shell=True)
        self.set(False)
        atexit.register(self.set, False)

    def set(self, bl_set):
        if bl_set:
            self.blanked = True
            bl_val = '1'
            self.logger.info('===================>>> Screen OFF')
        else:
            self.blanked = False
            bl_val = '0'
            self.logger.info('===================>>> Screen ON')
        if sys.platform != "win32":
            file = open(self.bl_ctl,'r+')
            file.seek(0)
            file.write(bl_val)
            file.close

    def is_blanked(self):
        return self.blanked

    def blank_screen(self, *args):
      self.set(True)

    def schedule(self):
      self.bl_event = Clock.schedule_once(self.blank_screen, self.bl_interval)

    def unschedule(self):
      self.bl_event.cancel()

    def on_window_touch_down(self, x, y):
      self.unschedule()
      self.schedule()
      if self.is_blanked():
        self.set(False)
        return True
      return False

    def start(self, bl_interval):
      if bl_interval > 0:
        self.bl_interval = bl_interval
        self.schedule()
        Window.bind(on_touch_down=self.on_window_touch_down)

    def stop(self):
      if self.bl_event != None:
        self.unschedule()
      self.set(False)

screen_blanker = Screen_Blanker()
