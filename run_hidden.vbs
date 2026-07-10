Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

Function FindExecutableOnPath(fileName)
    Dim pathValue, folder, candidate

    FindExecutableOnPath = ""
    pathValue = shell.ExpandEnvironmentStrings("%PATH%")

    For Each folder In Split(pathValue, ";")
        folder = Trim(folder)
        If Len(folder) >= 2 Then
            If Left(folder, 1) = """" And Right(folder, 1) = """" Then
                folder = Mid(folder, 2, Len(folder) - 2)
            End If
        End If

        If folder <> "" Then
            If Right(folder, 1) = "\" Then
                candidate = folder & fileName
            Else
                candidate = folder & "\" & fileName
            End If

            If fso.FileExists(candidate) Then
                FindExecutableOnPath = candidate
                Exit Function
            End If
        End If
    Next
End Function

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = scriptDir & "\launch_hidden.py"

localPythonwPath = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python314\pythonw.exe"
rootPythonwPath = "C:\Python314\pythonw.exe"
pathPywPath = FindExecutableOnPath("pyw.exe")
pathPythonwPath = FindExecutableOnPath("pythonw.exe")

If pathPywPath <> "" And fso.FileExists(pathPywPath) Then
    shell.Run """" & pathPywPath & """ -3 """ & scriptPath & """", 0, False
ElseIf fso.FileExists(localPythonwPath) Then
    shell.Run """" & localPythonwPath & """ """ & scriptPath & """", 0, False
ElseIf fso.FileExists(rootPythonwPath) Then
    shell.Run """" & rootPythonwPath & """ """ & scriptPath & """", 0, False
ElseIf pathPythonwPath <> "" And fso.FileExists(pathPythonwPath) Then
    shell.Run """" & pathPythonwPath & """ """ & scriptPath & """", 0, False
Else
    MsgBox "VPN Monitor cannot start because a required component is missing:" & _
        vbCrLf & vbCrLf & "- Python 3.9+ (pythonw.exe or pyw.exe)" & _
        vbCrLf & vbCrLf & "Install Python 3.9 or newer and try again.", _
        vbCritical, "VPN Monitor failed to start"
End If
