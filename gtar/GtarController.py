from consts import *
import Live
import time

from math import ceil

def RGBMValue(red, green, blue, msg):
	rgbmValue =  ((int(ceil((float(red) / 255.0) * 3)) & 0x3) << 6)
	rgbmValue += ((int(ceil((float(green) / 255.0) * 3)) & 0x3) << 4)
	rgbmValue += ((int(ceil((float(blue) / 255.0) * 3)) & 0x3) << 2)
	rgbmValue += ((int(ceil((float(msg) / 255.0) * 3)) & 0x3) << 0)
	return rgbmValue
	
def MRGBValue(msg, red, green, blue):	
	mrgbValue =  ((msg & 0x3) << 6)
	mrgbValue += ((int((float(red) / 255.0) * 3) & 0x3) << 4)
	mrgbValue += ((int((float(green) / 255.0) * 3) & 0x3) << 2)
	mrgbValue += ((int((float(blue) / 255.0) * 3) & 0x3) << 0)
	mrgbValue = mrgbValue & 0x7F
	return mrgbValue

class GtarController:
	"""
	The gTar Controller will control all the gTar specific functionality
	with the aid of the transport layer.  This is an implementation of the
	gTar Hardware Specification
	"""
	
	m_fStart = False
	
	m_Modes = ['live', 'record'];
	m_mode_n = 0;
	m_fRecording = False;
	
	def __init__(self, transport):
		""" gTar Controller Constructor """
		self.m_transport = transport
		#self.m_SongController = self.m_transport.m_SongController
		
	def Initialize(self):
		"""
		Sets up the gTar into a standard state
		"""
		self.m_transport.LogMessage("+GtarController::Initialize")
		self.SetNoteActive(0, 0, 0)
		self.SetFretFollow(0, 0, 0)
		self.SetLedRGBM(0, 0, 0, 0, 0, 0)		# This will clear the LEDs

		
		self.UpdateGtarDisplay()
		return self
		
	def UpdateGtarDisplay(self):
		self.DisplayDPad(1, GTAR_CTL_FRET_START)
		self.DisplayPlayStopButton()
		self.DisplayChangeModeButton()
		self.DisplayRecordButton()

	def DisplayRecordButton(self):
		if(self.m_mode_n == 0):
			self.SetLedExMRGB(2, GTAR_CTL_FRET_START + 1, 0, 0, 0, 0);
		if(self.m_mode_n == 1):
			if(not self.m_fRecording):
				self.SetLedExMRGB(2, GTAR_CTL_FRET_START + 1, 0, 255, 0, 0);
			else:
				self.SetLedExMRGB(2, GTAR_CTL_FRET_START + 1, 0, 0, 0, 255);
	
	def DisplayChangeModeButton(self):
		if(self.m_mode_n == 0):
			self.SetLedExMRGB(6, GTAR_CTL_FRET_START + 1, 0, 0, 0, 255);
		elif(self.m_mode_n == 1):
			self.SetLedExMRGB(6, GTAR_CTL_FRET_START + 1, 0, 255, 0, 0);
		
	def DisplayPlayStopButton(self):
		if(not self.m_fStart):
			self.SetLedExMRGB(6, GTAR_CTL_FRET_START + 0, 0, 0, 255, 0)
		else:
			self.SetLedExMRGB(6, GTAR_CTL_FRET_START + 0, 0, 255, 0, 0)
	
	def ToggleStartStop(self):
		self.m_fStart = not self.m_fStart
		if(self.m_fStart):
			self.m_transport.m_SongController.PlaySong()
		else:
			self.m_transport.m_SongController.StopSong()
		self.DisplayPlayStopButton()
		
	def HandleRecordButtonClick(self):
		if(self.m_mode_n == 1):
			if(not self.m_fRecording):
				self.m_transport.m_SongController.FireHighlightedSlot()
				self.m_fRecording = True
			else:
				self.m_transport.m_SongController.StopHighlightedSlot()
				self.m_fRecording = False
	
	def UpdateDisplay(self):
		self.m_transport.UpdateDisplay();
	
	def ToggleMode(self):
		self.m_transport.LogMessage("Toggle mode from: " + str(self.m_mode_n))
		self.m_mode_n += 1
		if(self.m_mode_n >= len(self.m_Modes)):
			self.m_mode_n = 0
		self.DisplayChangeModeButton()
		self.m_transport.RequestRebuildMidiMap()
		self.UpdateDisplay()
		self.UpdateGtarDisplay()
		
	def UpdatePlayStopButton(self, fState):
		self.m_fStart = fState
		self.DisplayPlayStopButton()
		
	def DisplayDPad(self, xPos, yPos):		
		time.sleep(0.001)
		self.SetLedExMRGB(xPos + 1, yPos + 0, 0, 255, 255, 255)
		time.sleep(0.001)
		self.SetLedExMRGB(xPos + 0, yPos + 1, 0, 255, 255, 255)
		time.sleep(0.001)
		self.SetLedExMRGB(xPos + 2, yPos + 1, 0, 255, 255, 255)
		time.sleep(0.001)
		self.SetLedExMRGB(xPos + 1, yPos + 2, 0, 255, 255, 255)
		
	def HandleMidiInput(self, MidiBytes):
		""" Handles Incoming MIDI data """
		status = MidiBytes[0] & 0xF0
		channel = MidiBytes[0] & 0x0F
		self.m_transport.LogMessage("MIDI IN status:" + hex(status) + " channel:" + str(channel))
		if(status == NOTE_ON_STATUS):
			note = MidiBytes[1]
			velocity = MidiBytes[2]
			self.m_transport.LogMessage("Rx midi on:" + str(note) + " vel: " + str(velocity));
			gStr = channel
			gFret = self.GtarMidiFret(channel, note)
			self.HandleGtarInput(gStr, gFret, velocity, MidiBytes)
		elif(status == NOTE_OFF_STATUS):
			note = MidiBytes[1]
			velocity = MidiBytes[2]
			self.m_transport.LogMessage("Rx midi off:" + str(note) + " vel: " + str(velocity));
			gStr = channel
			gFret = self.GtarMidiFret(channel, note)
			# No current use for the note off messages :(
		elif (status == CC_STATUS):
			cc_no = MidiBytes[1]
			cc_value = MidiBytes[2]
			self.m_transport.LogMessage("Rx cc midi no:" + str(cc_no) + " val: " + str(cc_value));
		else:
			self.m_transportLogMessage("Unhandled midi msg status: " + str(status))
			return None
	
	def GtarMidiFret(self, channel, note):
		gFret = note
		if(channel == 1):
			gFret -= 40
		elif(channel == 2):
			gFret -= 45
		elif(channel == 3):
			gFret -= 50
		elif(channel == 4):
			gFret -= 55
		elif(channel == 5):
			gFret -= 59
		elif(channel == 6):
			gFret -= 64
		return gFret
	
	# string is one based
	def GtarGetStringFretMidi(self, string, fret):
		gMidi = 40 + ((string - 1)*5) + fret;
		if(string > 4): 
			gMidi -= 1;
		return gMidi;
	
	def HandleGtarInput(self, gStr, gFret, velocity, MidiBytes):
		self.m_transport.LogMessage("Trigger str#: " + str(gStr) + " fret#: " + str(gFret))
		if(gStr != 0 and gFret != 0 and gFret < GTAR_CTL_FRET_START):
			if(self.m_mode_n == 0):
				if(velocity >= 0):	#will ensure low volume won't trigger - velocity not routing through correctly
					self.m_transport.m_SongController.TriggerFromStrFret(gStr, gFret)
			elif(self.m_mode_n == 1):
				self.m_transport.send_midi(MidiBytes)
		elif(gStr != 0 and gFret >= GTAR_CTL_FRET_START and gFret <= GTAR_CTL_FRET_END):
			relX = gStr - 1
			relY = gFret - GTAR_CTL_FRET_START
			self.HandleCtlAreaInput(relX, relY)
		else:
			return None
	
	def HandleCtlAreaInput(self, XPos, YPos):
		self.m_transport.LogMessage("Ctl Input x: " + str(XPos) + " y: " + str(YPos))
		if(XPos == 5 and YPos == 0):
			# This indicates the user hit the StartStop button
			self.ToggleStartStop()
		elif(XPos == 5 and YPos == 1):
				# This indicates the user hit the toggle mode button
				self.ToggleMode()
		elif(XPos == 0 and YPos == 1):
			# Left
			if(self.m_mode_n == 0):
				self.m_transport.m_SongController.MoveSessionByOffset(-1, 0)
			elif(self.m_mode_n == 1):
				self.m_transport.m_SongController.MoveArmTrackLeft()
		elif(XPos == 1 and YPos == 0):
			# Up
			if(self.m_mode_n == 0):
				self.m_transport.m_SongController.MoveSessionByOffset(0, -1)
			elif(self.m_mode_n == 1):
				self.m_transport.m_SongController.MoveHighlightedClipslotUp()
		elif(XPos == 1 and YPos == 2):
			# Down
			if(self.m_mode_n == 0):			
				self.m_transport.m_SongController.MoveSessionByOffset(0, 1)
			elif(self.m_mode_n == 1):
				self.m_transport.m_SongController.MoveHighlightedClipslotDown()
		elif(XPos == 2 and YPos == 1):
			# Right
			if(self.m_mode_n == 0):
				self.m_transport.m_SongController.MoveSessionByOffset(1, 0)
			elif(self.m_mode_n == 1):
				self.m_transport.m_SongController.MoveArmTrackRight()
		elif(XPos == 1 and YPos == 1):
			self.HandleRecordButtonClick()
			
		
	def SendControlChangeMsg(self, cc_no, value):
		SendMidiTuple = (CC_STATUS, cc_no, value)
		return self.m_transport.SendMidi(SendMidiTuple)

	def SendNoteOn(self, midi, velocity):
		SendMidiTuple = (NOTE_ON_STATUS, midi, velocity)
		return self.m_transport.SendMidi(SendMidiTuple)
		
	def SendNoteOff(self, midi, velocity):
		SendMidiTuple = (NOTE_OFF_STATUS, midi, velocity)
		return self.m_transport.SendMidi(SendMidiTuple)
	
	# This is unsafe and will send missing data	
	def SetLedRGBM(self, gStr, gFret, red, green, blue, msg):
		"""
		SetLedRGBM will send a SysEx based Set LED message 
		since the gTar only supports 6 bit color and the input 
		values are assumed to be [0, 255], the appropriate
		scaling is done
		"""		
		return self.SetLedExMRGB(gStr, gFret, msg, red, green, blue)		# re-route to the SysEx safe function
		#rgbmValue = RGBMValue(red, green, blue, msg)
		#SendMidiTuple = (GTAR_ID, SET_LED, (gStr & 0x7F), (gFret & 0x7F), (rgbmValue & 0x7F))
		#return self.m_transport.SendSysEx(SendMidiTuple)
		
	def SetLedExMRGB(self, gStr, gFret, msg, red, green, blue):
		"""
		SetLedMRGB will send a SysEx based Set LED Ex message 
		since the gTar only supports 6 bit color and the input 
		values are assumed to be [0, 255], the appropriate
		scaling is done.  This uses the corrected MRGB format
		to deal with the 0x7F range of SysEx data bytes
		"""		
		mrgbValue = MRGBValue(msg, red, green, blue)
		SendMidiTuple = (GTAR_ID, SET_LED_EX, (gStr & 0x7F), (gFret & 0x7F), (mrgbValue & 0x7F))
		return self.m_transport.SendSysEx(SendMidiTuple)
		
	def SetSlideState(self, SlideState):
		"""
		SetSlideState will set the slide state for the gTar
		Sliding should be turned off when the gTar is being used as a controller 
		"""
		safeSlideState = SlideState & 0x01
		self.m_transport.LogMessage("+GtarController::SetSlideState: " + hex(safeSlideState));		
		SendMidiTuple = (GTAR_ID, SET_SLIDE_STATE, (safeSlideState & 0x7F))
		return self.m_transport.SendSysEx(SendMidiTuple)		
		
	def SetNoteActive(self, red, green, blue):
		"""
		SetNoteActive will set the color of the Note Active gTar Mode
		"""
		rgbmValue = RGBMValue(red, green, blue, 0)
		self.m_transport.LogMessage("+GtarController::SetNoteActive: " + hex(rgbmValue));		
		SendMidiTuple = (GTAR_ID, SET_NOTE_ACTIVE, (rgbmValue & 0x7F))
		return self.m_transport.SendSysEx(SendMidiTuple)
		
	def SetFretFollow(self, red, green, blue):
		"""
		SetFretFollow will set the color of the Fret Follow gTar Mode
		"""
		rgbmValue = RGBMValue(red, green, blue, 0)
		self.m_transport.LogMessage("+GtarController::SetFretFollow: " + hex(rgbmValue));
		SendMidiTuple = (GTAR_ID, SET_FRET_FOLLOW, (rgbmValue & 0x7F))
		return self.m_transport.SendSysEx(SendMidiTuple)
	
	def Disconnect(self):
		self.SetLedRGBM(0, 0, 0, 0, 0, 0)		# This will clear the LEDs
		self.m_transport.LogMessage("+GtarController::Disconnect")
	
	def __del__(self):
		pass
		
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	