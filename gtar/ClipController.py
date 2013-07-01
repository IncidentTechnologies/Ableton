from consts import *
import Live

from GtarController import MRGBValue

class ClipController:
	"""
	The Clip Controller is what actually manipulates the clip 
	with reference to the gTar Controller
	"""
	
	def __init__(self, ClipSlotController, Clip):
		self.m_ClipSlotController = ClipSlotController
		self.m_Transport = self.m_ClipSlotController.m_Transport
		self.m_GtarController = self.m_Transport.m_GtarController
		self.m_Clip = Clip
		self.SetupClipHandlers()
		self.UpdateDisplay()
		
	def SetupClipHandlers(self):
		if not self.m_Clip:
			return None
		self.m_Clip.add_color_listener(self.OnClipColorChanged)
		self.m_Clip.add_playing_status_listener(self.OnClipPlayingChanged)
		self.m_Clip.add_looping_listener(self.OnClipLoopingChanged)
		
	def UpdateDisplay(self):
		if(not self.m_GtarController):
			return None
			
		relXPos = self.m_ClipSlotController.m_TrackController.m_TrackIndex - self.m_ClipSlotController.m_TrackController.m_SongController.m_SessionTrackOffset;	
		relXPos += 1	# Tracks are zero based, frets one based
		relYPos = self.m_ClipSlotController.m_ClipSlotIndex - self.m_ClipSlotController.m_TrackController.m_SongController.m_SessionSceneOffset
		relYPos += 1	# Scenes are zero based, strings one based
		
		if(not self.m_Clip or self.m_GtarController.m_mode_n != 0):
			self.m_GtarController.SetLedRGBM(relXPos, relYPos, 0, 0, 0, 0)
		elif(self.m_Clip.is_playing):
			self.m_GtarController.SetLedRGBM(relXPos, relYPos, 255, 255, 255, 0)
		else:
			color = self.m_Clip.color
			red = (color >> 16) & 0xFF
			green = (color >> 8) & 0xFF
			blue = (color >> 0) & 0xFF
			self.m_GtarController.SetLedRGBM(relXPos, relYPos, red, green, blue, 0)
		
	def RemoveClipHandlers(self):
		if not self.m_Clip:
			return None
		self.m_Clip.remove_color_listener(self.OnClipColorChanged)
		self.m_Clip.remove_playing_status_listener(self.OnClipPlayingChanged)
		self.m_Clip.remove_looping_listener(self.OnClipLoopingChanged)		
	
	def OnClipLoopingChanged(self):
		self.m_Transport.LogMessage("+OnClipLoopingChanged: " + str(self.m_Clip.looping))

	def OnClipPlayingChanged(self):
		self.m_Transport.LogMessage("+OnClipPlayingChanged"  + str(self.m_Clip.is_playing))
		self.UpdateDisplay()

	def OnClipColorChanged(self):
		""" Clip changed color handler"""
		color = self.m_Clip.color
		red = (color >> 16) & 0xFF
		green = (color >> 8) & 0xFF
		blue = (color >> 0) & 0xFF
		mrgb = MRGBValue(0, red, green, blue)
		self.m_Transport.LogMessage("+OnClipColorChanged (r, g, b):" + str(red) + ", " + str(green) + ", " + str(blue) + " mrgb: " + hex(mrgb))
		self.UpdateDisplay()
		
	def Disconnect(self):
		#self.m_Transport.LogMessage("+Clip::Disconnect")
		self.RemoveClipHandlers()
		self.m_Clip = None
		self.UpdateDisplay()
		
	def __del__(self):
		""" ClipController Deconstructor """
		#self.m_Transport.LogMessage("+ClipDeconstructor")
		pass
		
		
		
		
		
		
		
		
		