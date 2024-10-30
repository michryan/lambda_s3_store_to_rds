@echo off

REM Define paths
set "packageFolder=package"
set "mainFile=lambda_function.py"
set "initFile=__init__.py"
set "testFolder=test"
set "sourceFolder=src"
set "zipFileName=package.zip"


REM Remove the package folder if it exists
if exist "%packageFolder%" (
    rmdir -Force /S /Q "%packageFolder%"
)

REM Remove the zip file if it exists
if exist "%zipFileName%" (
    rm "%zipFileName%"
)

REM Create the package folder
mkdir "%packageFolder%"

REM Install the Pillow dependency into the package folder
echo Installing Pillow to the package folder...
pip install pillow --target="%packageFolder%"
pip install pymysql --target="%packageFolder%"


REM Copy the main file to the package folder
if exist "%mainFile%" (
    copy "%mainFile%" "%packageFolder%\"
) else (
    echo File '%mainFile%' does not exist.
)

REM Copy the init file to the package folder
if exist "%initFile%" (
    copy "%initFile%" "%packageFolder%\"
) else (
    echo File '%mainFile%' does not exist.
)

REM Copy the test folder to the package folder
if exist "%testFolder%" (
    xcopy "%testFolder%" "%packageFolder%\%testFolder%\" /E /I /Y
) else (
    echo Folder '%testFolder%' does not exist.
)

REM Copy the source folder to the package folder
if exist "%sourceFolder%" (
    xcopy "%sourceFolder%" "%packageFolder%\%sourceFolder%\" /E /I /Y
) else (
    echo Folder '%sourceFolder%' does not exist.
)


REM Zip the package folder
PowerShell -Command "Compress-Archive -Force -Path '%packageFolder%' -DestinationPath '%zipFileName%'"
echo Folder '%packageFolder%' has been zipped to '%zipFileName%'.
pause