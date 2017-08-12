# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin

from .File_Reader import File_Reader
from multiprocessing import Process, Pipe
import multiprocessing
#from threading import Timer, Thread
import traceback
import thread

#for saving meta data
import octoprint.filemanager
import sys
import os



class Meta_reader(octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.StartupPlugin,
                        octoprint.plugin.ShutdownPlugin,
                        octoprint.plugin.EventHandlerPlugin):

    def __init__(self, **kwargs):
        # super(Meta_Reader,self).__init__(**kwargs)
        self.printing = False
        self.spinning = False
        self.child_pipe, self.parent_pipe = Pipe()
        self.files = {}
        self.meta_process = Process(target = File_Reader, args=(self.child_pipe, self.files, ) )

    #for when Octoprint exits
    def on_shutdown(self):
        for child in multiprocessing.active_children():
            self._logger.info("Killed Child")
            child.terminate()
        self._logger.info("Meta Reader Terminated")
        
    
    def on_after_startup(self):
        self._logger.info("Starting the Meta Reader")


    def analyze_files(self, files={}, *args , **kwargs):
        self._logger.info("Spinning = " + str(self.meta_process.is_alive()))
        if self.meta_process.is_alive() == False:

            #Start the Meta Process
            self.files = files
            self.meta_process = Process(target = File_Reader, args=(self.child_pipe, self.files, ))
            self.spinning = True
            self._logger.info("Started Analyzing files")
            self.meta_process.start()

    #this function collects data from the pipe when it is available. It is fired off by a parent program
    #so it does not interfere with the UI Since they run within the same processing space
    def collect_meta_data(self):
        poll = self.parent_pipe.poll()
        if poll:
            collected_data = self.parent_pipe.recv()
            self._logger.info("Recieving Data From Process")
            if len(collected_data) > 0:
                self._logger.info("Collected Data: " + str(collected_data))
                if collected_data[0] != False:
                    self.save_data(collected_data[0], collected_data[1], collected_data[2])
                

    #This function will save meta data to the machine
    def save_data(self, data, filename, path):
        self._file_manager.set_additional_metadata(octoprint.filemanager.FileDestinations.LOCAL,
                                               path,
                                               'robo_data',
                                               data)

        
    def on_event(self,event, payload):

        if event == 'PrintStarted':
            self.printing = True
            self.parent_pipe.send(["Exit"])
    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
        )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/Meta_Reader.js"],
            css=["css/Meta_Reader.css"],
            less=["less/Meta_Reader.less"]
        )

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            Meta_Reader=dict(
                displayName="Meta_reader",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="Robo3d",
                repo="Meta-Reader",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/Robo3D/Meta-Reader/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Meta_reader"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Meta_reader()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

    global __plugin_helpers__
    __plugin_helpers__ = dict(start_analysis = __plugin_implementation__.analyze_files,
                              collect_data = __plugin_implementation__.collect_meta_data)
