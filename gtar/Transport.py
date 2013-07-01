#Transport.py

import Live # This allows us (and the Framework methods) to use the Live API on occasion
import time # We will be using time functions for time-stamping our log file outputs

from consts import *


from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.TransportComponent import TransportComponent # Class encapsulating all functions in Live's transport section
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller

from SongController import SongController
from GtarController import GtarController

class Transport(ControlSurface):
	__module__ = __name__
	__doc__ = "Test gTar Ableton Control Surface Mapping"
	
	session = None
	m_tracks_n = 6
	m_scenes_n = 16
	
	# Pre Init member vars
	m_SongController = None
	m_GtarController = None

	def __init__(self, c_instance):
		"""gTar Control Surface Initializer"""
		ControlSurface.__init__(self, c_instance)
		self.LogMessage("-- gTar Opened --")
		self._setup_transport_control() 	
		self.m_c_instance = c_instance;	
		self.m_app = Live.Application.get_application() # get a handle to the App

		# Set up the gTar Control first since the live set may need to access
		# the hardware right away
		self.m_GtarController = GtarController(self)
		self.m_GtarController.Initialize()

		# Set up the song control 
		self.m_SongController = SongController(self, 6, 12, 0, 0)
		
		# show console success
		maj = self.m_app.get_major_version() 
		min = self.m_app.get_minor_version() 
		bug = self.m_app.get_bugfix_version()
		self.ShowDebugMessage(str(maj) + "." + str(min) + "." + str(bug) + " started successfully") 
	
	def GetHandle(self):
		return self.m_c_instance.handle()
		
	# Only enable this in DEBUG mode
	def ShowDebugMessage(self, str):
		if DEBUG:
			self.show_message(str)
		else:
			return None
	
	def UpdateDisplay(self):
		if(self.m_SongController):
			self.m_SongController.UpdateDisplay();
		
	# Only enable this in DEBUG mode (Defined in consts.py)
	def LogMessage(self, str):
		if DEBUG:
			self.log_message(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + " " + str)
		else:
			return None
	
	def RequestRebuildMidiMap(self):
		return self.m_c_instance.request_rebuild_midi_map() 
	
	def SendMidi(self, SendBytesTuple):
		return self.send_midi(SendBytesTuple)
	
	def send_midi(self, midi_event_bytes):
	    return self.m_c_instance.send_midi(midi_event_bytes)
	
	def SendSysEx(self, SysExBytes):
		SysExMsg = (SYSEX_BEGIN,) + SysExBytes + (SYSEX_END,)
		return self.SendMidi(SysExMsg)
	
	# This function kicks off the creation of the midi map
	def build_midi_map(self, midi_map_handle):
		self.LogMessage("+build_midi_map")
		map_mode = Live.MidiMap.MapMode.absolute
		
		#self.LogMessage(str(dir(Live.MidiMap.map_midi_note)))
		#self.LogMessage(str(Live.MidiMap.map_midi_note.__doc__))
		
		# Build the midi-map for channels 0 - 6 for all CC messages
		for channel in range(6 + 1):
			for CC in range(127):
				Live.MidiMap.forward_midi_cc(self.GetHandle(), midi_map_handle, channel, CC)
				
		# Build the midi-map for channels 0 - 6 for all MIDI messages
		for channel in range(6 + 1):
			if(self.m_GtarController.m_mode_n == 0):
				for MIDI in range(127):
					Live.MidiMap.forward_midi_note(self.GetHandle(), midi_map_handle, channel, MIDI)
			elif(self.m_GtarController.m_mode_n == 1):
				for MIDI in range(127):
					gFret = self.m_GtarController.GtarMidiFret(channel, MIDI)
					if(gFret >= GTAR_CTL_FRET_START):
						Live.MidiMap.forward_midi_note(self.GetHandle(), midi_map_handle, channel, MIDI)
				
		self.LogMessage("-build_midi_map")
		return None
		
	
	def receive_midi(self, midi_bytes):
		return self.m_GtarController.HandleMidiInput(midi_bytes)

	def _setup_transport_control(self):
		"""Setup the Transport Control"""
		transport = TransportComponent() #Instantiate a Transport Component

	def disconnect(self):
		"""Clean up on disconnect"""
		if(self.m_GtarController is not None):
			self.m_GtarController.Disconnect()
			del self.m_GtarController
			self.m_GtarController = None
			
		if(self.m_SongController is not None):
			self.m_SongController.Disconnect()
			del self.m_SongController
			self.m_SongController = None		
		# Disconnect Control Surface 
		ControlSurface.disconnect(self)
		# Done!
		self.LogMessage("-- gTar Closed --") 
		
		
		
		
		
		
		