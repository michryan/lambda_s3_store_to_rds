#!/bin/bash

# Define paths
packageFolder="package"
mainFile="lambda_function.py"
initFile="__init__.py"
testFolder="test"
sourceFolder="src"
zipFileName="package.zip"

# Remove the package folder if it exists
if [ -d "$packageFolder" ]; then
    rm -rf "$packageFolder"
fi

# Remove the zip file if it exists
if [ -f "$zipFileName" ]; then
    rm "$zipFileName"
fi

# Create the package folder
mkdir "$packageFolder"

# Install the Pillow and pymysql dependencies into the package folder
echo "Installing Pillow to the package folder..."
pip install pillow --target="$packageFolder"
pip install pymysql --target="$packageFolder"

# Copy the main file to the package folder
if [ -f "$mainFile" ]; then
    cp "$mainFile" "$packageFolder/"
else
    echo "File '$mainFile' does not exist."
fi

# Copy the init file to the package folder
if [ -f "$initFile" ]; then
    cp "$initFile" "$packageFolder/"
else
    echo "File '$initFile' does not exist."
fi

# Copy the test folder to the package folder
if [ -d "$testFolder" ]; then
    cp -r "$testFolder/" "$packageFolder/$testFolder/"
else
    echo "Folder '$testFolder' does not exist."
fi

# Copy the source folder to the package folder
if [ -d "$sourceFolder" ]; then
    cp -r "$sourceFolder/" "$packageFolder/$sourceFolder/"
else
    echo "Folder '$sourceFolder' does not exist."
fi

# Zip the package folder
zip -r "$zipFileName" "$packageFolder"
echo "Folder '$packageFolder' has been zipped to '$zipFileName'."