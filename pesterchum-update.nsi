
; The name of the installer
Name "PESTERCHUM3.14a"

; The file to write
OutFile "pesterchum3.14a0.2update.exe"

RequestExecutionLevel admin

Page components
Page instfiles

; The stuff to install
Section "Pesterchum"

  SectionIn RO

  ReadRegStr $INSTDIR HKLM "SOFTWARE\Pesterchum" "Install_Dir"

  StrCmp $INSTDIR "" error
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r themes
  File /r smilies
  File library.zip
  File pesterchum.exe
  
  Delete "$SMPROGRAMS\Pesterchum\Pesterchum.lnk"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Pesterchum.lnk" "$INSTDIR\pesterchum.exe"
   
  Goto done
  error:
    MessageBox MB_OK "Pesterchum not found on this machine!"
  done:

SectionEnd
