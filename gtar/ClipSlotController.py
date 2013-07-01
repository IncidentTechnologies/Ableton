from consts import *
import Live

from ClipController import ClipController

class ClipSlotController:
	"""
	The ClipSlotController will set up the appropriate 
	listeners and callbacks to indicate when a given
	ClipSlot has been altered
	"""
	
	m_ClipController = None
	
	def __init__(self, TrackController, ClipSlot, ClipSlotIndex):
		""" ClipSlot Constructor """
		self.m_TrackController = TrackController
		self.m_Transport = self.m_TrackController.m_Transport
		self.m_GtarController = self.m_Transport.m_GtarController
		self.m_ClipSlot = ClipSlot
		self.m_ClipSlotIndex = ClipSlotIndex
		self.SetupClipSlotHandlers()
		self.UpdateClip()
		
	def SetupClipSlotHandlers(self):
		if not self.m_ClipSlot:
			return None
		self.m_ClipSlot.add_has_clip_listener(self.OnHasClipChanged)
		
	def RemoveClipSlotHandlers(self):
		if not self.m_ClipSlot:
			return None
		self.m_ClipSlot.remove_has_clip_listener(self.OnHasClipChanged)	

	def UpdateClip(self):
		if(self.m_ClipSlot.has_clip and self.m_ClipSlot.clip is not None):
			#self.m_Transport.LogMessage("Creating ClipController at ClipSlot#:" + str(self.m_ClipSlotIndex) + " on track#: " + str(self.m_TrackController.m_TrackIndex))
			self.m_ClipController = ClipController(self, self.m_ClipSlot.clip)
		else:
			self.ClearClip()
			
	def UpdateDisplay(self):
		if(self.m_ClipController):
			self.m_ClipController.UpdateDisplay();

	def Trigger(self):
		if(self.m_ClipSlot):
			self.m_ClipSlot.fire()
		else:
			return None	
	
	def ClearClip(self):
		if(self.m_ClipController is not None):
			#self.m_Transport.LogMessage("+ClearClip at ClipSlot#:" + str(self.m_ClipSlotIndex) + " on track#: " + str(self.m_TrackController.m_TrackIndex))
			self.m_ClipController.Disconnect()
			del self.m_ClipController
			self.m_ClipController = None	
	
	def OnHasClipChanged(self):
		self.m_Transport.LogMessage("+OnHasClipChanged " + str(self.m_ClipSlot.has_clip));		
		self.UpdateClip()
		
	def Disconnect(self):
		#self.m_Transport.LogMessage("+ClipSlot::Disconnect track#:" + str(self.m_ClipSlotIndex))		
		self.ClearClip()		
		
	def __del__(self):
		#self.m_Transport.LogMessage("+ClipSlotDeconstructor track#:" + str(self.m_ClipSlotIndex))		
		pass








