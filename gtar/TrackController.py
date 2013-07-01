from consts import *
import Live

from _Framework.SessionComponent import SessionComponent

from ClipSlotController import ClipSlotController

class TrackController:
	"""
	The track controller keeps tracks organized and also
	sets up all of the ClipSlots organized and sets up
	their listeners.  It makes more sense to give the tracks
	this responsibility than the scenes considering the Live
	Object Model has strong pairing with the clips / tracks and weak
	pairing with the scenes
	"""
	
	# The ClipSlots
	m_ClipSlots = None
	
	def __init__(self, SongController, LiveTrack, TrackIndex):
		""" Track Controller Constructor """
		self.m_SongController = SongController
		self.m_Transport = self.m_SongController.m_transport
		self.m_GtarController = self.m_Transport.m_GtarController
		self.m_LiveTrack = LiveTrack
		self.m_TrackIndex = TrackIndex
		self.SetupTrackHandlers()			# Track specific handlers
		self.SetupClipSlots()				# ClipSlots
		
	def SetupTrackHandlers(self):
		if not self.m_LiveTrack:
			return None
		self.m_LiveTrack.add_clip_slots_listener(self.OnClipSlotsChanged)
		
	def TriggerClipSlot(self, gFret):
		if(self.m_ClipSlots and gFret <= len(self.m_ClipSlots)):
			triggerClipSlot = self.m_ClipSlots[gFret - 1]
			triggerClipSlot.Trigger()
		else:
			return None
		
	def SetupClipSlots(self):
		self.ClearClipSlots()
		startClipIndex = self.m_SongController.m_SessionSceneOffset
		endClipIndex = self.m_SongController.m_SessionSceneOffset + self.m_SongController.m_NumSessionScenes
		if(endClipIndex >= len(self.m_LiveTrack.clip_slots)):
			endClipIndex = len(self.m_LiveTrack.clip_slots) - 1
		
		#for i in range(len(self.m_LiveTrack.clip_slots)):
		for i in range(startClipIndex, endClipIndex):
			clipSlot = self.m_LiveTrack.clip_slots[i]
			newClipSlot = ClipSlotController(self, clipSlot, i)
			self.m_ClipSlots.append(newClipSlot)
			
	def UpdateDisplay(self):
		for clipslot in self.m_ClipSlots:
			clipslot.UpdateDisplay();
			
	def ClearClipSlots(self):
		if(self.m_ClipSlots and len(self.m_ClipSlots) > 0):
			for clipSlot in self.m_ClipSlots:
				clipSlot.Disconnect()
				del clipSlot
				clipSlot = None
		self.m_ClipSlots = []	
	
	def RemoveTrackHandlers(self):
		if not self.m_LiveTrack:
			return None
		self.m_LiveTrack.remove_clip_slots_listener(self.OnClipSlotsChanged)
			
	def OnClipSlotsChanged(self):
		self.m_Transport.LogMessage("+OnClipSlotsChanged")
		
	def Disconnect(self):
		#self.m_Transport.LogMessage("+TrackController::Disconnect track#:" + str(self.m_TrackIndex))
		self.ClearClipSlots()
		self.RemoveTrackHandlers()
		
	def __del__(self):
		#self.m_Transport.LogMessage("+TrackControllerDeconstructor track#:" + str(self.m_TrackIndex))
		pass
		
		
		
		