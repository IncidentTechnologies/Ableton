Connect the gTar to Ableton!
============================

The gTar Ableton scripts are an unoffical set of scripts we've developed internally that allow the gTar to interoperate with Ableton beyond just being a traditional midi controller. Some of the functions include the ability to trigger loops and samples, as well as flip back and forth from live play mode and even record clips that can then be used to loop over and then manipulated by the triggering mode. The functionality developed is similar to what can be done with the APC40 or Ableton Push.

Installation

To install the script, copy all of the files in this directory into a new folder in the following path:

AbletonApplicationFolder/Live.app/Contents/App-Resources/MIDI Remote Script/gTar

You might have to create the gTar folder. You could also name it a different name, whatever you name it will be what pops up in the preferences sceen in Ableton.

Usage

Once the files are placed in the correct spot in the filesystem start Ableton. Go to Preferences->MIDI Sync. You will need to turn on the gTar input MIDI device to Track and Remote for both input/output in the MIDI Ports section. Once this is done you can choose one of the Control surface rows and assign the input/output to the gTar. Then on the left scroll down and choose the gTar (or whatever you named your folder to) and this should now connect Ableton to the gTar.

The red bounding box shows where the Ableton active region.

We plan to develop some deeper support for this script in the future, but for now most of the functionality is APC40 like, but there is also a way to switch between live/record mode by hitting the blue fret in the control area on the gTar.

The 4 white LEDs in the control are are effectively a D-pad to control the bounding box, or if you're in record mode to change the active instrument. In record mode the red button in the center of the D-pad will trigger the slot you're in, so if the track is armed and the slot empty it will start to record a clip, and if you're in the process of recording it will stop recording. Once recording is done hitting the center again will trigger that sample.

For any questions, issues, or bug reports, please contact us at dev@incidenttech.com
