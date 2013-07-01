# Global debug flag
DEBUG = 1
#DEBUG = 0


# MIDI Specific Stuff
NOTE_OFF_STATUS = 	0x80
NOTE_ON_STATUS 	= 	0x90
CC_STATUS 		= 	0xB0

SYSEX_BEGIN 	=	0xF0
SYSEX_END 		= 	0xF7

# GTAR Specific 
GTAR_ID		=	0x77

# gTar Messages
SET_LED				= 	0x00
SET_LED_EX			= 	0x0A
SET_NOTE_ACTIVE		=	0x01
SET_FRET_FOLLOW		=	0x02
SET_SLIDE_STATE		=	0x0B

# gTar Ableton Control
GTAR_MSTR_TRACK_FRET	=	13		# This fret can act as a kill for the track
GTAR_CTL_FRET_START 	=	14
GTAR_CTL_FRET_END		=	16