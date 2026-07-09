Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python314\pythonw.exe"
scriptPath = scriptDir & "\vpn_monitor.py"

If fso.FileExists(pythonwPath) Then
    shell.Run """" & pythonwPath & """ """ & scriptPath & """", 0, False
Else
    shell.Run "cmd /c cd /d """ & scriptDir & """ && run.bat", 0, False
End If
