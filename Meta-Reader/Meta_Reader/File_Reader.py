import subprocess
import re
import sys
import os
import os.path
import traceback
import time
from multiprocessing import Pipe
import logging


class File_Reader():
    def __init__(self, child_pipe, file_dict):
        self.cpipe = child_pipe
        if sys.platform == "win32":
            logging.basicConfig(filename='C:\\Users\\mauro\\AppData\\Roaming\\OctoPrint\\logs\\octoprint.log', level=logging.DEBUG)
        else:
            logging.basicConfig(filename='/home/pi/.octoprint/logs/octoprint.log', level=logging.DEBUG)
        self.logger = logging
        self.logger.info("File Reader Started")
        self.files = file_dict
        self.needed_updates = {}
        self.update()

    def update(self):
        self.logger.info("Started a process at " + str(os.getpid()))
        if self.files == {}:
            self.logger.info("Process " + str(os.getpid()) +" Exiting" )
            sys.exit()
            return
        
        try:
            #initialize list
            self.check_files()

            #analyze list
            self.length_of_updates = len(self.needed_updates)
            while self.length_of_updates > 0:
                #analyze files
                self.analyze_files()

                #check if we need to update list
                if self.cpipe.poll():
                    #get files
                    files = self.cpipe.recv()
                    self.logger.info("Files Recieved")
                    #process added files
                    self.recursive_file_check(files, 0) 
                    self.length_of_updates = len(self.needed_updates)                
                
            self.logger.info("Process " + str(os.getpid()) +" Exiting" )
            sys.exit()

        except Exception as e:
            self.logger.info("!!!!!!!!!!!!!!!!!!!Exception: " + str(e))
            traceback.print_exc()
            self.logger.info("Process " + str(os.getpid()) +" Exiting" )
            sys.exit()

    def check_saved_data(self, entry):
        saved_data = entry
    
        if 'robo_data' in saved_data:
            return saved_data['robo_data']
        else:
            return False

    #This function will save meta data to the machine
    def save_data(self, data, filename, path):
        robodata = [data, filename, path]
        self.cpipe.send(robodata)



    def check_files(self):
        #list all files        
        self.recursive_file_check(self.files, 0)

    def recursive_file_check(self, folder, depth):
        if type(folder) is dict:
            #protection against a max recursion depth error
            if depth > 50:
                self.logger.info("Max Recursion Depth Reached. Why do you have folders 50 layers deep?")
                return
    
            for file in folder:
                if folder[file]['type'] == 'machinecode':
                    if self.check_saved_data(folder[file]) != False:
                        pass
                    elif folder[file]['path'] not in self.needed_updates:
                        if sys.platform == "win32":
                            path = "C:\\Users\\mauro\\AppData\\Roaming\\OctoPrint\\uploads\\" + folder[file]['path']
                        else:
                            path = "/home/pi/.octoprint/uploads/" + folder[file]['path']
                        self.logger.info("adding: " + path + " Rec Depth = " + str(depth))
                        self.needed_updates[folder[file]['path']] = path

                elif folder[file]['type'] == 'folder' and 'children' in folder[file]:
                    new_folder = folder[file]['children']
                    self.recursive_file_check(new_folder, depth + 1)

    def analyze_files(self):
        if len(self.needed_updates) > 0:
            key = self.needed_updates.iterkeys().next()
            path = self.needed_updates[key]
            del self.needed_updates[key]
            self.logger.info("Analyzing file: " + str(key))

            try:
                self.detirmine_slicer(path, key)
            except Exception as e:
                self.logger.info("!!!!!!!!!!!!!!!!!!!Exception: " + str(e))
                traceback.print_exc()
                #delete all pending files since they will be regenerated
                del self.needed_updates
                self.needed_updates = {}
                return
        else:
            return False              

    def detirmine_slicer(self,filename, path):
        cura = ";Generated with Cura_SteamEngine ([0-9.]+)"
        simplify3d = "Simplify3D"
        meta = None

        #read first 10 lines to detirmine slicer
        with open(filename, 'r') as file:
            for x in range(0,10):
                line  = file.readline()
            
                _cura = re.findall(cura, line)
                _simplify = re.findall(simplify3d, line)
                
            
                if _cura != []:
                    #self.logger.info("Sliced with Cura")

                    #if _cura[0] == '15.04':
                    if (_cura[0].find('15.04', 0, 5) >= 0):
                        self.logger.info("Sliced with old cura " + str(_cura[0]))
                        meta = self.cura_1504_reader(filename)
                        break
                    else:
                        self.logger.info("Sliced with new cura " + str(_cura[0]))
                        meta = self.cura_meta_reader(filename)
                        break

                elif _simplify != []:
                    #self.logger.info("Sliced with Simplify 3D")
                    meta = self.simplify_meta_reader(filename)
                    break

                

               
        if meta == None:
            self.logger.info("Using Empty Data")
            meta = {
                'layer height' : "--",
                'layers' : "--",
                'infill' : "--",
                'time' : {'hours': '0', 
                          'minutes': '0',
                          'seconds': '0'
                          }
            }
            self.save_data(meta, filename, path)
            return meta
        elif meta != None:
            self.logger.info("Using saved Data")
            
            self.save_data(meta, filename, path)
            return meta
        

    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def cura_meta_reader(self, _filename):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        _hours = "0"
        _minutes = "0"
        _seconds = "0"
        _time = 0
        _time_dict = {}

        meta = {}

        cura_lh = "layer_height = ([0-9.]+)"
        cura_ls = ";LAYER_COUNT:([0-9.]+)"
        cura_in = "sparse_density = ([0-9.]+)"
        cura_time = ";TIME:([0-9.]+)"
        identifier = ";End of Gcode"

        record_meta = False
        raw_meta = ""

       
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    _cura_ls = re.findall(cura_ls, line)
                    _cura_time = re.findall(cura_time, line)
                    
                    if _cura_ls != []:
                        _layers = int(_cura_ls[0])

                    if _cura_time != []:
                        _time = int(_cura_time[0])
                        _time_dict = self.parse_time(_time)
                        _hours = _time_dict['hours']
                        _minutes = _time_dict['minutes']
                        _seconds = _time_dict['seconds']

                    if re.match(identifier, line):
                        record_meta = True

                    if record_meta:
                        raw_meta += line
                    

        #This block makes the raw meta readable to the re functions
        raw_meta = raw_meta.replace(";SETTING_3 ", "")
        raw_meta = raw_meta.replace(identifier, "")
        raw_meta = raw_meta.replace("\\\\n", " ")
        raw_meta = raw_meta.replace("layer_height_0", "layer_height")
        raw_meta = raw_meta.splitlines()

        new_meta = ''
        for line in raw_meta:
            new_meta += line

        _cura_in = re.findall(cura_in, new_meta)
        _cura_lh = re.findall(cura_lh, new_meta)
        if _cura_lh != []:
            _layer_height = float(_cura_lh[0])

        if _cura_in != []: 
            _infill = float(_cura_in[0])
        
            
        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill,
            'time' : {'hours': str(_hours), 
                      'minutes': str(_minutes),
                      'seconds': str(_seconds)
                      }
        }
        return meta


    def cura_1504_reader(self, _filename):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        _hours = "0"
        _minutes = "0"
        _seconds = "0"
        _time = 0
        _time_dict = {}

        meta = {}

        cura_lh = "; layer height = ([0-9.]+)"
        cura_ls = ";Layer count: ([0-9.]+)"
        cura_in = "; infill = ([0-9.]+)"
        cura_time = "; time = ([0-9.]+)"
        

        record_meta = False
        raw_meta = ""

       
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    _cura_ls = re.findall(cura_ls, line)
                    _cura_time = re.findall(cura_time, line)
                    _cura_lh = re.findall(cura_lh, line)
                    _cura_in = re.findall(cura_in, line)
                    
                    if _cura_ls != []:
                        _layers = int(_cura_ls[0])

                    if _cura_time != []:
                        _time = int(_cura_time[0])
                        _time_dict = self.parse_time(_time)
                        _hours = _time_dict['hours']
                        _minutes = _time_dict['minutes']
                        _seconds = _time_dict['seconds']

                    if _cura_lh != []:
                        _layer_height = float(_cura_lh[0])

                    if _cura_in != []:
                        _infill = int(_cura_in[0])

                    
        
            
        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill,
            'time' : {'hours': str(_hours), 
                      'minutes': str(_minutes),
                      'seconds': str(_seconds)
                      }
        }
        return meta




    # This takes a number in seconds and returns a dictionary of the hours/minutes/seconds
    def parse_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)

        time_dict = {'hours': str(h),
                     'minutes': str(m),
                     'seconds': str(s)
                     }

        return time_dict




    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def simplify_meta_reader(self, _filename):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        _hours = "0"
        _minutes = "0"
        meta = {}

        s3d_lh = ";   layerHeight,([0-9.]+)"
        s3d_ls = "; layer ([0-9.]+)"
        s3d_in = ";   infillPercentage,([0-9.]+)"

        #looks like ;   Build time: 3 hours 5 minutes

        s3d_time = ";   Build time: ([0-9.]+) hours ([0-9.]+) minutes"
        s3d_time2 = ";   Build time: ([0-9.]+) hour ([0-9.]+) minutes"
        s3d_time3 = ";   Build time: ([0-9.]+) hour ([0-9.]+) minute"
        s3d_time4 = ";   Build time: ([0-9.]+) hours ([0-9.]+) minute"

        #read first 200 lines for Layer height
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    
                    _s3d_lh = re.findall(s3d_lh, line)
                    _s3d_ls = re.findall(s3d_ls, line)
                    _s3d_in = re.findall(s3d_in, line)
                    _s3d_time = re.findall(s3d_time, line)
                    _s3d_time2 = re.findall(s3d_time2, line)
                    _s3d_time3 = re.findall(s3d_time3, line)
                    _s3d_time4 = re.findall(s3d_time4, line)
                   
    
                    if _s3d_lh != []:
                        _layer_height = float(_s3d_lh[0])
    
                    if _s3d_ls != []:
                        _layers = int(_s3d_ls[0])

                    if _s3d_in != []:
                        _infill = int(_s3d_in[0])

                    if _s3d_time != []:
                        _hours = _s3d_time[0][0]
                        _minutes = _s3d_time[0][1]

                    if _s3d_time2 != []:
                        _hours = _s3d_time2[0][0]
                        _minutes = _s3d_time2[0][1]

                    if _s3d_time3 != []:
                        _hours = _s3d_time3[0][0]
                        _minutes = _s3d_time3[0][1]
                        
                    if _s3d_time4 != []:
                        _hours = _s3d_time4[0][0]
                        _minutes = _s3d_time4[0][1]

                    

        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill,
            'time' : {'hours': str(_hours), 
                          'minutes': str(_minutes),
                          'seconds': '0'
                          }
        }
        return meta

