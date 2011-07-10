#!/bin/bash

## Cleanup
rm -rf build/ dist/
rm -f Pesterchum.dmg

### Force build with custom installed frameworky python not system python
/Library/Frameworks/Python.framework/Versions/2.6/bin/python setup-py2app.py py2app
#python setup-py2app.py py2app
#
### Do some .app tings
touch dist/Pesterchum.app/Contents/Resources/qt.conf
find dist/Pesterchum.app -iname "*_debug" -exec rm -f '{}' \;

## Create a dmg file to hold everything
VERSION=$(python version.py)    #"3.41.2 Beta 5"
SIZE=2000
name="Pesterchum"
title="${name} ${VERSION}"
CHANGELOG="Changelog.rtf"
PYQUIRKS="Python Quirks.rtf"
TODO="To Do.rtf"
README="Read Me!.rtf"
## Make a proper installer dmg not just effectively a zip file.
#
# Most of this is from http://stackoverflow.com/questions/96882/
# I've fiddled with it a little

# Store the background picture (in PNG format) in a folder called ".background"
# in the DMG, and store its name in the "backgroundPictureName" variable.

mkdir dist/.background
cp MacBuild/dmg_background.png dist/.background/display.png

# Convert markdown files to rich text files
convert=~/Library/Haskell/bin/pandoc
if ! test -e "${convert}"
then
    echo "Please install pandoc from http://johnmacfarlane.net/pandoc/" 1>&2
    exit 1
fi

echo "Converting CHANGELOG . . . "
$convert --standalone --smart --from=markdown --to=rtf --output="dist/${CHANGELOG}" CHANGELOG.mkdn
echo "Converting PYQUIRKS . . ."
$convert --standalone --smart --from=markdown --to=rtf --output="dist/${PYQUIRKS}" PYQUIRKS.mkdn
echo "Converting TODO . . ."
$convert --standalone --smart --from=markdown --to=rtf --output="dist/${TODO}" TODO.mkdn
echo "Converting README . . ."
$convert --standalone --smart --from=markdown --to=rtf --output="dist/${README}" README.mkdn

# Create a R/W DMG. It must be larger than the result will be.
# In this example, the bash variable "size" contains the size
#  in Kb and the contents of the folder in the "source" bash
#  variable will be copied into the DMG:
# Note: I've removed the size argument

echo "Creating initial DMG file . . ."
hdiutil create -srcfolder "./dist" -volname "${title}" -fs HFS+ \
      -fsargs "-c c=64,a=16,e=16" -format UDRW pack.temp.dmg

# Mount the disk image, and store the device name
#  (you might want to use sleep for a few seconds after this operation):

echo "Mounting initial DMG file . . ."
device=$(hdiutil attach -readwrite -noverify -noautoopen "pack.temp.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')
sleep 2



# Use AppleScript to set the visual styles (name of .app must be in bash variable
# "applicationName", use variables for the other properties as needed):
base=100
iconsize=72
padding=18
echo "Making DMG file pretty with Applescript . . ."
echo '
   tell application "Finder"
     tell disk "'${title}'"
           open
           set current view of container window to icon view
           set toolbar visible of container window to false
           set statusbar visible of container window to false
           set the bounds of container window to {400, 100, 885, 430}
           set theViewOptions to the icon view options of container window
           set arrangement of theViewOptions to not arranged
           set icon size of theViewOptions to 72
           set background picture of theViewOptions to file ".background:display.png"
           make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
           -- Positions
           set position of item "'${name}'.app" of container window to {100, 100}
           set position of item "Applications" of container window to {375, 100}
           set position of item "'${README}'" of container window to    {'${base}+${iconsize}*0+${padding}*0', 244}
           set position of item "'${CHANGELOG}'" of container window to {'${base}+${iconsize}*1+${padding}*1', 244}
           set position of item "'${PYQUIRKS}'" of container window to  {'${base}+${iconsize}*2+${padding}*2', 244}
           set position of item "'${TODO}'" of container window to      {'${base}+${iconsize}*3+${padding}*3', 244}
           -- Visibility
           set extension hidden of item "'${CHANGELOG}'" of container window to true
           set extension hidden of item "'${PYQUIRKS}'" of container window to true
           set extension hidden of item "'${TODO}'" of container window to true
           set extension hidden of item "'${README}'" of container window to true
           close
           open
           update without registering applications
           delay 5
           eject
     end tell
   end tell
' | osascript

# This took so long to work out how to do ._.
# Stolen from http://lists.apple.com/archives/darwin-userlevel/2007/Oct/msg00000.html
# Set the SLA to read only (dunno why)
echo "Converting initial DMG file to a UDRO one . . ."
hdiutil convert -ov -format UDRO -o "sla.temp.dmg" "pack.temp.dmg"
# Inflate the dmg
echo "Inflating UDRO DMG file . . ."
hdiutil unflatten "sla.temp.dmg"
# Attach the GPL
echo "Attaching GPL licence . . ."
Rez -a MacBuild/GPL.res -o "sla.temp.dmg"
# Steamroller again
echo "Deflating UDRO DMG file . . ."
hdiutil flatten "sla.temp.dmg"

# Finialize the DMG by setting permissions properly, compressing and releasing it:

#chmod -Rf go-w /Volumes/"${title}"
sync
#hdiutil detach ${device}
echo "Compressing UDRO DMG file to UDZO for release . . ."
hdiutil convert "sla.temp.dmg" -format UDZO -imagekey zlib-level=6 -o "${name}.dmg"

# Get rid of the bits
echo "Cleaning up . . ."
rm -f pack.temp.dmg 
rm -f sla.temp.dmg
rm -rf build/ dist/
