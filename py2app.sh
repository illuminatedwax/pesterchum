#!/bin/sh
rm -rf build/ dist/
python setup-py2app.py py2app
touch dist/pesterchum.app/Contents/Resources/qt.conf
find dist/pesterchum.app -iname "*_debug" -exec rm -f '{}' \;
rm -rf Pesterchum
mv dist Pesterchum
rm -f pesterchum.dmg
hdiutil create pesterchum.dmg -srcdir Pesterchum -format UDZO
