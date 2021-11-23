@echo off
    setlocal
    set KILL01=Zoom*

:execute
    for /F "usebackq tokens=2" %%a in (`tasklist /fi "IMAGENAME eq %KILL01%" ^| findstr "[0-9]"`) do @set RESULT=%%a
    taskkill /f /pid %RESULT%
    for /F "usebackq tokens=2" %%a in (`tasklist /fi "IMAGENAME eq %KILL01%" ^| findstr "[0-9]"`) do @set RESULT=%%a
    taskkill /f /pid %RESULT%

:end
    endlocal