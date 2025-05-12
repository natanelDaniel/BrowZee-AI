!define MUI_WELCOMEPAGE_TITLE "Welcome to Browzee Setup"
!define MUI_WELCOMEPAGE_TEXT "Setup will guide you through the installation of Browzee.\r\n\r\nIt is recommended that you close all other applications before starting Setup. This will make it possible to update relevant system files without having to reboot your computer.\r\n\r\nClick Next to continue."
!define MUI_FINISHPAGE_TITLE "Browzee Installation Complete"
!define MUI_FINISHPAGE_TEXT "Browzee has been successfully installed on your computer."

; --- הגדרות בסיס ---
OutFile "BrowzeeSetup.exe"
InstallDir "$PROGRAMFILES\Browzee"
RequestExecutionLevel admin

; --- עמודי אשף ---
!include "MUI2.nsh"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

; ----------  התקנה  ----------
Section "Install Browzee" SEC01
  SetOutPath $INSTDIR
  File /r "browzee_dist\*.*"

  ; קיצור דרך
  CreateShortcut "$DESKTOP\Browzee.lnk" "$INSTDIR\browzee.exe"
  CreateDirectory "$SMPROGRAMS\Browzee"
  CreateShortcut "$SMPROGRAMS\Browzee\Browzee.lnk" "$INSTDIR\browzee.exe"

  ; כתובת ההתקנה ברג'יסטרי – עכשיו בתוך Section
  WriteRegStr HKCU "Software\Browzee" "Install_Dir" "$INSTDIR"
SectionEnd

; ----------  הסרה  ----------
Section "Uninstall"
  Delete "$DESKTOP\Browzee.lnk"
  Delete "$SMPROGRAMS\Browzee\Browzee.lnk"
  Delete "$INSTDIR\server2.exe"
  Delete "$INSTDIR\browzee.exe"
  RMDir /r "$INSTDIR"
  RMDir "$SMPROGRAMS\Browzee"

  ; ניקוי הרג'יסטרי
  DeleteRegKey HKCU "Software\Browzee"
SectionEnd
