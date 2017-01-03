# -*- coding: utf-8 -*-
#
#       pvg_common.py
#
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

#       Revisions by Caitlin Laughrey and Loretta E Laughrey in 2016.


# ----------------------------------------------------------------------------   Imports
import wx, os
import cv2, cv
import ConfigParser                     # configuration file handler
import datetime
from dateutil import parser
import wx.lib.newevent
import pysolovideo as pv


ThumbnailClickedEvt, EVT_THUMBNAIL_CLICKED = wx.lib.newevent.NewCommandEvent()

"""
--------------------------------------------------------------------------   Developer Settings
"""
call_tracking = False  # if True each function will report it's beginning and end
show_imgs = False  # if true, show images

DEFAULT_data_dir = '\\Documents\\GitHub\\LL-DAM-Analysis\\Data\\Working_files\\'
DEFAULT_configfile = 'pysolo_video.cfg'
pDir = (os.environ['USERPROFILE']) + DEFAULT_data_dir


# -------------------------------------------------------------------------------  Config Object
class Configuration:
    """
    Handles program configuration
    Uses ConfigParser to store and retrieve
    From gg's toolbox
    """
    def __init__(self, filename=None):

        """
        filename    the name of the configuration file
        config      configuration class object
                    options     pertain to program operation
                    monitors    pertain to video source
        self.config dictionary containing all config parameters and their values, indexed on 'section, key'

        read        reads configuration file and creates config dictionary
        getValue    retrieves value from the configuration class object using section and key
        setValue    sets an new value for a key from config dictionary
        save        saves configuration to a file
        """
        self.pDir = pDir
        self.getFilename(filename)          # gets or creates a valid filename for the config file and creates one if there is no config file
        self.getConfigObj()                 # reads the config file
        self.getConfigDict()                # creates dictionary of config options for easy reference

        return
# %% ----------------------------------------------------------- get file name for configuration
    def getFilename(self, filename):
        self.full_filename = filename
    # make sure folder is accessible  & make a new config file there
        if os.access(self.full_filename, os.W_OK):
            self.pDir = os.path.split(self.full_filename)[0]
            return                                 # valid filename given, no need to create a default configuration

        if not os.access(self.pDir, os.W_OK):             # if not accessible use default directory
            os.makedirs(self.pDir)

        if filename is None:                              # if no filename use default filename
            self.full_filename =  os.path.join(self.pDir, DEFAULT_configfile)

        if filename == os.path.split(filename)[1] :       # a filename was given without a path:  create a file with default options in default path
            self.full_filename = os.path.join(self.pDir, filename)

        self.defaultConfig()             # create a default dictionary


# %% ----------------------------------------------------------  Create configuration dictionary from scratch and create file
    def defaultConfig(self):

        self.configDict = {
            'Options, webcams': 0,
            'Options, thumbnailsize': (320, 240),
            'Options, fullsize': (640, 480),
            'Options, fps_preview': 5,
            'Options, monitors': 1,
            'Options, pDir': (os.path.split(self.full_filename)[0]),
            'Monitor1, mon_name': 'Monitor1',
            'Monitor1, sourcetype': 1,
            'Monitor1, issdmonitor': False,
            'Monitor1, source': None,
            'Monitor1, fps_recording': 1,
            'Monitor1, start_datetime': datetime.datetime.now(),
            'Monitor1, track': False,
            'Monitor1, tracktype': 0,
            'Monitor1, maskfile': None,
            'Monitor1, output_folder': None
        }

    # save to file
        self.save_Config(self.full_filename, new=True)
#  ---------------------------------------------------------------------- reads the config file to make the config_obj
    def getConfigObj(self):

        self.config_obj = ConfigParser.RawConfigParser()                    # read the config file
        self.config_obj.read(self.full_filename)
# -----------------------------------------------------------------------  create configuration dictionary
    def getConfigDict(self):
        """
        Create dictionary from config_obj for easier lookup of configuration info
        """
        self.configDict = {}

    # Options
        self.opt_keys = ['webcams', 'thumbnailsize', 'fullsize',  'fps_preview', 'monitors', 'pDir']

        if not self.config_obj.has_section('Options'):
            self.config_obj.add_section('Options')

        for key in self.opt_keys:
            if not self.config_obj.has_option('Options',key):
                self.config_obj.set('Options', key, None)
            value = self.getValue('Options', key)               # TODO:  are we doing this twice without need?
            indexStr = 'Options, ' + key
            self.configDict[indexStr] = value

    #Monitors
        self.mon_keys = ['sourcetype','issdmonitor', 'source','fps_recording','start_datetime','track','tracktype','maskfile','output_folder']

        if not self.config_obj.has_option('Options','monitors'):
            n_mons = 0
        else:
            n_mons = int(self.config_obj.get('Options','monitors'))

        for m in range(1, n_mons+1 ):
                mon_name = 'Monitor%d' % m
                for key in self.mon_keys:
                    if not self.config_obj.has_option(mon_name, key):
                        self.config_obj.set(mon_name, key, None)
                    value = self.getValue(mon_name, key)
                    indexStr = mon_name + ', ' + key
                    self.configDict[indexStr] = value




# %%  ----------------------------------------------------------------------------  Save config file
    def save_Config(self, filename=DEFAULT_configfile, new=False):

        """
        Saves the configuration dictionary to full_filename.
        """
        if new:
            self.config_obj = ConfigParser.RawConfigParser()
            self.config_obj.add_section('Options')
            self.config_obj.add_section('Monitor1')

    # update configuration object with current config dictionary
        opt_keys = ['webcams', 'thumbnailsize', 'fullsize', 'fps_preview', 'monitors', 'pDir']
        for key in opt_keys:
            self.config_obj.set('Options', key, self.configDict['Options, '+key])

        mon_keys = ['sourcetype','issdmonitor', 'source','fps_recording','start_datetime','track','tracktype','maskfile','output_folder']
        if self.configDict['Options, monitors'] > 0:
            for mon_num in range(1, self.configDict['Options, monitors']):
                mon_name = 'Monitor%d' % mon_num
                for key in mon_keys:
                    self.config_obj.set(mon_name, key, self.configDict[mon_name + ', '+key])

    # save to file
        with open(filename, 'wb') as configfile:
            self.config_obj.write(configfile)


# %% ------------------------------------------------------------------------------------ Save file as
    def onFileSaveAs(self):

        """
        Opens the save file window
        """

        # set file types for find dialog
        wildcard = "PySolo Video config file (*.cfg)|*.cfg|" \
                   "All files (*.*)|*.*"  # adding space in here will mess it up!

        dlg = wx.FileDialog(self,
                            message="Save file as ...", defaultDir=self.configDict['Options, pDir'],
                            defaultFile=os.path.split(self.full_filename)[1], wildcard=wildcard,
                            style=(wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                            )

        if dlg.ShowModal() == wx.ID_OK:  # show the save window
            self.full_filename = dlg.GetPath()  # gets the path from the save dialog
            self.save_Config(self.full_filename, new=False)  # TODO:  save is writing a blank file

        dlg.Destroy()


        # %%
# %% ------------------------------------------------------------------------------------ Open file
    def onFileOpen(self):  # viewing all files is not an option

        """                                                                    # .cfg files don't show.  you can ask for it, but it doesn't load
        Opens the open file window                                              # no complaints about non-existent files
        """
        #  set file types for find dialog
        wildcard = "pySolo Video config file (*.cfg)|*.cfg|" \
                   " All files (*.*)|*.*"  # don't add any spaces!

        dlg = wx.FileDialog(  # make an open-file window
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:  # show the open-file window
            path = dlg.GetPath()
            self.__init__(path)

        dlg.Destroy()


    # %% ----------------------------------------------------------  Set Values in Config
    def setValue(self, section, key, value):

        """
        changes or adds a configuration value in config file
        """
        if not self.config_obj.has_section(section):
            self.config_obj.add_section(section)
        if not self.config_obj.has_option(section, key):
            self.config_obj.set(section, key)

        self.config_obj.set(section, key, value)


    # %%  -----------------------------------------------------------------------------------  Get values from config
    def getValue(self, section, key):

        """
        get value from config file based on section and keyword
        Do some sanity checking to return tuple, integer and strings, datetimes, as required.
        """

        #
        if  not self.config_obj.has_option(section, key):                       # does option exist?
            r = None
            return r

        r = self.config_obj.get(section, key)

        if r == 'None' or r == None:                                                        # None type
            r = None
            return r

        if key == 'start_datetime' and type(r) == type(''):                     # datetime values
            try: r = parser.parse(r)
            except: r = datetime.datetime.now()

            return r

    # look for string characteristics to figure out what type they should be
        if r == 'True' or r == 'False' :                                         # boolean
            if r == 'False' :
                r = False
            elif r == 'True' :
                r = True

            return r

        try:
            int(r) == int(0)                                                   # int
            return int(r)
        except Exception:
            pass

        try:
            float(r) == float(1.1)                                              # float
            return float(r)
        except Exception:
            pass

        if ',' in r:                                                         # tuple of two integers
            if not '(' in r:
                r = '(' + r + ')'
            r = tuple(r[1:-1].split(','))
            r = (int(r[0]), int(r[1]))

            return r

        return r                                                             # all else has failed:  return as string


"""                         UNUSED?
class pvg_config(Configuration):
    """"""
    Inheriting from myConfig
    """"""
    def __init__(self, filename=None, temporary=False):


        defaultOptions = {
            "Monitors" :      [9, "Select the number of monitors connected to this machine"],
            "Webcams"  :      [1, "Select the number of webcams connected to this machine"],
            "ThumbnailSize" : ['320, 240', "Specify the size for the thumbnail previews"],
            "FullSize" :      ['640, 480', "Specify the size for the actual acquisition from the webcams.\nMake sure your webcam supports this definition"],
            "FPS_preview" :   [5, "Refresh frequency (FPS) of the thumbnails during preview.\nSelect a low rate for slow computers"],
            "FPS_recording" : [5, "Actual refresh rate (FPS) during acquisition and processing"],
            "Data_Folder" :   [pDir, "Folder where the final data are saved"]
             }

        self.monitorProperties = ['sourceType', 'source', 'track', 'maskfile', 'trackType', 'isSDMonitor']

        myConfig.__init__(self, filename, temporary, defaultOptions)


    def SetMonitor(self, monitor, *args):

       mn = 'Monitor%s' % monitor
        for v, vn in zip( args, self.monitorProperties ):
            self.SetValue(mn, vn, v)


    def GetMonitor(self, monitor):

        mn = 'Monitor%s' % monitor
        md = []
        if self.config.has_section(mn):
            for vn in self.monitorProperties:
                md.append ( self.GetValue(mn, vn) )

        return md

    def HasMonitor(self, monitor):

        mn = 'Monitor%s' % monitor
        a = self.config.has_section(mn)

        return a

    def getMonitorsData(self):

        """"""
        return a list containing the monitors that we need to track
        based on info found in configfile
        """"""
        monitors = {}

        ms = self.GetOption('Monitors')
        resolution = self.GetOption('FullSize')
        dataFolder = self.GetOption('Data_Folder')

        for mon in range(0,ms):
            if self.HasMonitor(mon):
                _,source,track,mask_file,track_type,isSDMonitor = self.GetMonitor(mon)
                monitors[mon] = {}
                monitors[mon]['source'] = source
                monitors[mon]['resolution'] = resolution
                monitors[mon]['mask_file'] = mask_file
                monitors[mon]['track_type'] = track_type
                monitors[mon]['dataFolder'] = dataFolder
                monitors[mon]['track'] = track
                monitors[mon]['isSDMonitor'] = isSDMonitor


        return monitors
"""