
; The name of the installer
Name "PESTERCHUM3.41"

; The file to write
OutFile "pesterchum3.41.exe"

InstallDir C:\Pesterchum

InstallDirRegKey HKLM "Software\Pesterchum" "Install_Dir"
RequestExecutionLevel admin

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles


; The stuff to install
Section "Pesterchum"

  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r *.*
  Rename $INSTDIR\README.mkdn $INSTDIR\readme.txt
  Rename $INSTDIR\CHANGELOG.mkdn $INSTDIR\changelog.txt

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\Pesterchum "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pesterchum" "DisplayName" "PESTERCHUM"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pesterchum" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pesterchum" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pesterchum" "NoRepair" 1
  WriteUninstaller "uninstall.exe"

  CreateDirectory "$SMPROGRAMS\Pesterchum"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Pesterchum.lnk" "$INSTDIR\pesterchum.exe"
  CreateShortcut "$DESKTOP\Pesterchum.lnk" "$INSTDIR\pesterchum.exe"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Readme.lnk" "$INSTDIR\readme.txt"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  CreateShortcut "$SMPROGRAMS\Pesterchum\Logs.lnk" "$LOCALAPPDATA\pesterchum\logs"
SectionEnd

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pesterchum"
  DeleteRegKey HKLM SOFTWARE\Pesterchum

  ; Remove files and uninstaller
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Pesterchum\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\Pesterchum"
  RMDir /r "$INSTDIR"

SectionEnd
