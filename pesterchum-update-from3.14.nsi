
; The name of the installer
Name "PESTERCHUM3.14 to 3.41"

; The file to write
OutFile "pesterchum3.14to3.41.exe"

RequestExecutionLevel admin

Page components
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

; The stuff to install
Section "Pesterchum"

  SectionIn RO

  ReadRegStr $INSTDIR HKLM "SOFTWARE\Pesterchum" "Install_Dir"

  StrCmp $INSTDIR "" error
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Check and see if this is really 3.14
  IfFileExists library.zip 0 error

  ClearErrors
  CreateDirectory $TEMP\pesterchum_backup
  IfErrors backuperror 0
  CopyFiles $INSTDIR\pesterchum.js $TEMP\pesterchum_backup
  CopyFiles $INSTDIR\profiles $TEMP\pesterchum_backup
  CopyFiles $INSTDIR\logs $TEMP\pesterchum_backup
  IfErrors cantcopy 0

  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Pesterchum\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\Pesterchum"
  RMDir /r "$INSTDIR"

  ; Put file there
  File /r *.*
  Rename $INSTDIR\README.mkdn $INSTDIR\readme.txt
  Rename $INSTDIR\CHANGELOG.mkdn $INSTDIR\changelog.txt

  ; Copy backup files
  ClearErrors
  CopyFiles $TEMP\pesterchum_backup\*.* $INSTDIR
  IfErrors brokeinstall 0
  RMDIR /r "$TEMP\pesterchum_backup"

  WriteUninstaller "uninstall.exe"

  CreateDirectory "$SMPROGRAMS\Pesterchum"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Pesterchum.lnk" "$INSTDIR\pesterchum.exe"
  CreateShortcut "$DESKTOP\Pesterchum.lnk" "$INSTDIR\pesterchum.exe"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Readme.lnk" "$INSTDIR\readme.txt"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortcut "$SMPROGRAMS\Pesterchum\Logs.lnk" "$LOCALAPPDATA\pesterchum\logs"

  Goto done

  error:
    MessageBox MB_OK "Pesterchum 3.14 (or 3.41 beta) not found on this machine!"
    Goto done
  backuperror:
    IfFileExists $TEMP\pesterchum_backup brokeinstall cantmaketmp
  cantmaketmp:
    MessageBox MB_OK "Error! Can't make temporary directory (to save your files) for some raisin. Check your privileges?? i dunno tbqh, soryr *sorry"
    Goto done
  brokeinstall:
    MessageBox MB_OK "Broken install detected. Please copy the files in $TEMP\pesterchum_backup to some place safe and then delete that folder."
    Goto done
  cantcopy:
    MessageBox MB_OK "Can't seem to copy Pesterchum backup files to temp directory."
    Goto done
  done:

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