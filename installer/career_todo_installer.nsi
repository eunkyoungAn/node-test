; Simple NSIS installer for CareerTodo
; Assumes the built EXE is at ../dist_icon/CareerTodoIcon.exe

Name "CareerTodo"
OutFile "career_todo_installer.exe"
InstallDir "$PROGRAMFILES\CareerTodo"
RequestExecutionLevel user

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File "..\dist_icon\CareerTodoIcon.exe"
  CreateDirectory "$SMPROGRAMS\CareerTodo"
  CreateShortCut "$SMPROGRAMS\CareerTodo\CareerTodo.lnk" "$INSTDIR\CareerTodoIcon.exe"
  CreateShortCut "$DESKTOP\CareerTodo.lnk" "$INSTDIR\CareerTodoIcon.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\CareerTodoIcon.exe"
  Delete "$SMPROGRAMS\CareerTodo\CareerTodo.lnk"
  Delete "$DESKTOP\CareerTodo.lnk"
  RMDir "$SMPROGRAMS\CareerTodo"
  RMDir "$INSTDIR"
SectionEnd
