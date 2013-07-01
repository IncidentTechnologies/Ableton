from consts import *
import Live

from _Framework.SessionComponent import SessionComponent 
from TrackController import TrackController

class SongController:
	"""
	The Song Controller listens to all of the changes in the 
	song composition such as the adding of new tracks, scenes, and clips.
	"""
	
	# Session Parameters
	m_NumSessionTracks = 6
	m_NumSessionScenes = 12
	m_SessionTrackOffset = 0
	m_SessionSceneOffset = 0
	m_Session = None 
	
	# Song Information
	m_NumScenes = None
	m_NumTracks = None	
	
	# Live tracks
	m_Tracks = None
	
	def __init__(self, transport, NumSessionTracks, NumSessionScenes, SessionTrackOffset, SessionSceneOffset):
		""" Song Controller Constructor """
		self.m_song = Live.Application.get_application().get_document()
		self.UpdateSong()
		self.m_transport = transport
		self.SetupSongHandlers()
		self.SetupSession(NumSessionTracks, NumSessionScenes, SessionTrackOffset, SessionSceneOffset)
		self.SetupTracks()
		
	def UpdateSong(self):
		self.m_NumTracks = len(self.m_song.tracks)
		self.m_NumScenes = len(self.m_song.scenes)		
	
	def Disconnect(self):
		self.m_transport.LogMessage("+SongController::Disconnect")
		self.ClearTracks()
		self.RemoveSongHandlers()
		
	def FindHighlightedTrack(self):
		slot = self.m_song.view.highlighted_clip_slot
		i = 0;
		j = 0;
		#self.m_transport.LogMessage(str(slot))
		for track in self.m_song.tracks:
			for clipslot in track.clip_slots:
				if(slot == clipslot):
					return (i, j)
				j += 1
			i += 1
			j = 0
		return (-1,-1);
		
	def GetSlot(self, trackNum, rowNum):
		i = 0;
		j = 0;
		
		for track in self.m_song.tracks:
			if(i == trackNum):
				for clipslot in track.clip_slots:
					if(rowNum == j):
						return clipslot
					j += 1
			i += 1
		return None
		
	def FireHighlightedSlot(self):
		self.m_song.view.highlighted_clip_slot.fire()
		
	def StopHighlightedSlot(self):
		self.m_song.view.highlighted_clip_slot.stop()
		
	
		
	def HighlightSlot(self, track, row):
		slot = self.GetSlot(track, row)
		self.m_transport.LogMessage(str(slot))
		if(slot):
			self.m_song.view.highlighted_clip_slot = slot
		return slot
		
	def FindFirstArmedTrackIndex(self):
		i = 0;
		for track in self.m_song.tracks:			
			if(track.arm):
				self.m_transport.LogMessage("Found arm track: " + str(i))
				track.arm = False;
				return i;
			i += 1
		self.m_transport.LogMessage("No armed tracks found")
		return -1
		
	def MoveHighlightedClipslotDown(self):
		slotTuple = self.FindHighlightedTrack()
		col = slotTuple[0]
		row = slotTuple[1] + 1
		if(row >= len(self.m_song.tracks[col].clip_slots)):
			row = 0
		self.HighlightSlot(col, row)
		
	def MoveHighlightedClipslotUp(self):
		slotTuple = self.FindHighlightedTrack()
		col = slotTuple[0]
		row = slotTuple[1] - 1
		if(row < 0):
			row = len(self.m_song.tracks[col].clip_slots) - 1
		self.HighlightSlot(col, row)

	def MoveArmTrackLeft(self):
		index = self.FindFirstArmedTrackIndex();
		row = self.FindHighlightedTrack()[1]
		if(index != -1 and index > 0):
			self.m_song.tracks[index].arm = False;
			index -= 1;
			self.m_song.tracks[index].arm = True;
		elif(index == -1):
			index = len(self.m_song.tracks) - 1
			self.m_song.tracks[index].arm = True;
		self.HighlightSlot(index, row)	
			
	def MoveArmTrackRight(self):
		index = self.FindFirstArmedTrackIndex();
		row = self.FindHighlightedTrack()[1]
		if(index != -1 and index < len(self.m_song.tracks) - 1):
			self.m_song.tracks[index].arm = False;
			index += 1;
			self.m_song.tracks[index].arm = True;
		elif(index == -1):
			index = 0
			self.m_song.tracks[index].arm = True;
		self.HighlightSlot(index, row)	
			
	
	def SetupSession(self, NumSessionTracks, NumSessionScenes, SessionTrackOffset, SessionSceneOffset):
		"""Setup the session control"""
		self.m_NumSessionTracks = NumSessionTracks
		self.m_NumSessionScenes = NumSessionScenes
		self.m_SessionTrackOffset = SessionTrackOffset
		self.m_SessionSceneOffset = SessionSceneOffset
		self.m_Session = SessionComponent(self.m_NumSessionTracks, self.m_NumSessionScenes) 
		self.m_Session.set_offsets(self.m_SessionTrackOffset, self.m_SessionSceneOffset)
		
	def MoveSessionByOffset(self, XOffset, YOffset):
		self.m_transport.LogMessage("Moving Session by (x, y): " + str(XOffset) + ", " + str(YOffset))			
		self.ClearTracks()		# clear the tracks		
		self.m_SessionTrackOffset += XOffset
		if(self.m_SessionTrackOffset < 0):
			self.m_SessionTrackOffset = 0
		self.m_SessionSceneOffset += YOffset
		if(self.m_SessionSceneOffset < 0):
			self.m_SessionSceneOffset = 0
		# Update the session	
		self.m_Session.set_offsets(self.m_SessionTrackOffset, self.m_SessionSceneOffset)
		self.SetupTracks()
		
	def TriggerFromStrFret(self, gStr, gFret):
		if(self.m_Tracks and gStr <= len(self.m_Tracks)):
			triggerTrack = self.m_Tracks[gStr - 1]
			triggerTrack.TriggerClipSlot(gFret)
		else:
			return None
		
	def ClearTracks(self):
		if(self.m_Tracks and len(self.m_Tracks) > 0):
			for track in self.m_Tracks:
				track.Disconnect()
				del track
				track = None
		self.m_Tracks = []		
		
	def SetupTracks(self):
		self.m_Tracks = []
		for i in range(self.m_SessionTrackOffset, self.m_SessionTrackOffset + self.m_NumSessionTracks):
			if i >= len(self.m_song.tracks):
				break
			else:
				self.m_transport.LogMessage("Setup Track #:" + str(i))
				newTrack = TrackController(self, self.m_song.tracks[i], i)
				self.m_Tracks.append(newTrack)

	def UpdateDisplay(self):
		for track in self.m_Tracks:
			track.UpdateDisplay();
	
	def SetupSongHandlers(self):
		if not self.m_song:
			return None
		self.m_song.add_is_playing_listener(self.OnSongPlayingChanged)
		self.m_song.add_tracks_listener(self.OnSongTracksChanged)
		self.m_song.add_scenes_listener(self.OnSongScenesChanged)
		
	def RemoveSongHandlers(self):
		if not self.m_song:
			return None
		self.m_song.remove_is_playing_listener(self.OnSongPlayingChanged)
		self.m_song.remove_tracks_listener(self.OnSongTracksChanged)
		self.m_song.remove_scenes_listener(self.OnSongScenesChanged)
		
	def PlaySong(self):
		self.m_song.start_playing()

	def StopSong(self):
		self.m_song.stop_playing()		
				
	def OnSongPlayingChanged(self):		
		self.m_transport.LogMessage("+OnSongPlayingChanged")
		self.m_transport.m_GtarController.UpdatePlayStopButton(self.m_song.is_playing)
		
	def OnSongTracksChanged(self):
		self.m_transport.LogMessage("+OnSongTracksChanged")
		NumTracks = len(self.m_song.tracks)
		if NumTracks != self.m_NumTracks:
			self.m_NumTracks = NumTracks
			self.m_transport.LogMessage("New # of tracks: " + str(self.m_NumTracks))
		
	
	def OnSongScenesChanged(self):
		self.m_transport.LogMessage("+OnSongScenesChanged")
		NumScenes = len(self.m_song.scenes)
		if NumScenes != self.m_NumScenes:
			self.m_NumScenes = NumScenes
			self.m_transport.LogMessage("New # of scenes: " + str(self.m_NumScenes))	
			
	def __del__(self):
		pass
			
			
			
	
		