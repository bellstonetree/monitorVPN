Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = scriptDir & "\launch_hidden.py"

localPythonwPath = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python314\pythonw.exe"
rootPythonwPath = "C:\Python314\pythonw.exe"
pathPythonwPath = ""

Set whereResult = shell.Exec("cmd /c where pythonw 2>nul")
If Not whereResult.StdOut.AtEndOfStream Then
    pathPythonwPath = whereResult.StdOut.ReadLine()
End If

If fso.FileExists(localPythonwPath) Then
    shell.Run """" & localPythonwPath & """ """ & scriptPath & """", 0, False
ElseIf fso.FileExists(rootPythonwPath) Then
    shell.Run """" & rootPythonwPath & """ """ & scriptPath & """", 0, False
ElseIf pathPythonwPath <> "" And fso.FileExists(pathPythonwPath) Then
    shell.Run """" & pathPythonwPath & """ """ & scriptPath & """", 0, False
Else
    MsgBox "VPN Monitor could not find pythonw.exe." & vbCrLf & vbCrLf & _
        "Run run.bat to see troubleshooting details, or install Python 3.", _
        vbCritical, "VPN Monitor failed to start"
End If
