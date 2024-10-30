# Lambda S3 Store to Rds #
This conatins the code for a Lambda that will, upon receiving an S3 create event, upload the image stored into and RDS table. See belove for deployment instructions, assumptions, and testing details.

## Using this package ##

Use this package with one of the following: 
* powershell terminal on windows
* terminal on unix (MacOS, Linux)
* IDE of choice

This package and instructions were created using powershell on windows, and VSCode IDE

## Testing ##
To run the unit tests, navigate to the home directory of the package.  Navigate into the test folder with

` cd .\test\ `

Execute tests by running 

`python handle_image_store_test.py`

## Deployment Assumptions ##
This package assumes the user has an active AWS account with an S3 bucket, an RDS DataBase, and the appropriate roles and permissions to access each given to a lambda execution role. It is assumed there is a lambda trigger created listening to put events for the bucket in question, pointed to an dummy lambda.  It is assumed the RDS database contains a table with the following columns

```
1. ImageID 
2. FileName 
3. FileSize 
4. FileType 
5. Width 
6. Height 
7. Timestamp
```

## Deployment ##

### Assemble Package ###

This script uses a build script to assemble the needed Lambda zip file. From the home directory of the package, run the build script. If using windows powershell, run

``` 
Start-Process build.bat 
```

If using unix terminal, run

```
chmod +x build.sh
bash build.sh
```
This will create the package.zip file that will be uploaded in the following steps.

### AWS Console Upload ###

1. In the Functions page of the Lambda console, choose the function you want to upload the .zip file for.
2. Select the Code tab.
3. In the Code source pane, choose Upload from.
4. Choose .zip file.
5. Select Upload, then select the package.zip file in the file chooser.
6. Choose Open.
7. Choose Save.