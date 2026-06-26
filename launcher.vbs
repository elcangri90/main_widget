Set shell = CreateObject("WScript.Shell")

' === Launch HTA access key window ===
shell.Run "mshta.exe """ & Replace(WScript.ScriptFullName, WScript.ScriptName, "") & "accesskey.hta""", 1, True

' === Read access key from registry ===
On Error Resume Next
entered = shell.RegRead("HKCU\Software\TempAccessKey\Value")
On Error GoTo 0

' === Check access key ===
If entered <> "Maradona90" Then
    MsgBox "Incorrect key. Access denied.", 16, "Error"
    WScript.Quit
End If

' === Launch Python script ===
shell.Run """C:\Users\raffaele.beffa\Documents\python\1_so_list\venv\Scripts\python.exe"" ""C:\Users\raffaele.beffa\Documents\python\1_so_list\SO_list.py""", 0, False

' === Clean up registry ===
shell.RegDelete "HKCU\Software\TempAccessKey\Value"
