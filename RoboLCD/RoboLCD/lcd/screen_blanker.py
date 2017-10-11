import sys
import subprocess
import atexit
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.logger import Logger

class Screen_Blanker():
    """Manage screen blanking"""

    def __init__(self):
        self.bl_event = None
        self.blanked = False
        self.bl_interval = 0
        self.bl_ctl = '/sys/devices/platform/rpi_backlight/backlight/rpi_backlight/bl_power'
        if sys.platform != "win32":
            subprocess.call('sudo chmod 666 ' + self.bl_ctl, shell=True)
        self.stop()
        atexit.register(self.stop)

    def _set(self, bl_set):
        if bl_set:
            self.blanked = True
            bl_val = '1'
            Logger.info('Screen_Blanker: Screen OFF')
        else:
            self.blanked = False
            bl_val = '0'
            Logger.info('Screen_Blanker: Screen ON')
        if sys.platform != "win32":
            file = open(self.bl_ctl,'r+')
            file.seek(0)
            file.write(bl_val)
            file.close

    def _schedule(self):
      self.bl_event = Clock.schedule_once(lambda dt: self._set(True), self.bl_interval)

    def _unschedule(self):
      self.bl_event.cancel()

    def _on_window_touch_down(self, x, y):
      self._unschedule()
      self._schedule()
      if self.blanked:
        self._set(False)
        return True
      return False

    def start(self, bl_interval):
      """Start blanking system. Screen will blank after bl_interval seconds."""
      if bl_interval > 0:
        self.bl_interval = bl_interval
        self._schedule()
        Window.bind(on_touch_down=self._on_window_touch_down)

    def stop(self):
      """Shutdown blanking system."""
      if self.bl_event != None:
        self._unschedule()
      self._set(False)

screen_blanker = Screen_Blanker()

if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.button import Button

    class Test(App):
        def build(self):
            screen_blanker.start(10)

    Test().run()
