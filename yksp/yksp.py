#! /usr/bin/env python
'''
Copyright (C) 2014 Benedict Lau

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import sys
import os
import shutil
import signal
import subprocess
import time
import datetime
import re

try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewClient    

############
# Constants
############
FILENAME_DEVICE_SERIALS = 'serials.txt'
FILENAME_DEVICE_PROPERTIES = 'device.txt'
FILENAME_LOGCAT = 'logcat.txt'
FILENAME_PYUNIT = 'pyunit.txt'
FILENAME_APP_DATA_BACKUP = 'data.ab'

FOLDER_APP_DATA = 'data'
FOLDER_SCREENSHOTS = 'screenshots'
FOLDER_SCREENDUMPS = 'screendumps'

DIR_TEST_SCRIPTS = 'scripts'
DIR_TEST_RESULTS = 'results'
DIR_TEST_SESSION = '%s/%s' % (DIR_TEST_RESULTS, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S'))

PACKAGE_BACKUP_CONFIRM = 'com.android.backupconfirm'
ID_BUTTON_BACKUP_ACCEPT = 'id/no_id/21'

##########
# Methods
##########
def validate(value):
    '''
    Terminates execution if value=False. Does nothing otherwise.

    @type value: boolean
    @param value: The value to validate.
    '''
    if value is False:
        sys.exit(0)

def execCommand(cmd, msg=None, wait=True):
    '''
    Executes shell command in a subprocess.

    @type cmd: str
    @param cmd: The shell command to execute.
    @type msg: str
    @param msg: An optional message to print to stdout.
    @type wait: boolean
    @param wait: True to block execution until the subprocess finishes.
    @return: The tuple (subprocess running the command, stdoutdata, stderrdata). If wait=False, stdoutdata and stderrdata are None. 
    '''
    if msg:
        print msg
    if wait:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdData = p.communicate()
        returnData = (p, stdData[0], stdData[1])
    else:
        # Attach session id to use process group for terminating child process
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        returnData = (p, None, None)
    return returnData

def findApk():
    '''
    Scan for APK.

    @return: The APK filename; or None if not found.
    '''
    apkFilename = None
    print 'Scanning for APK...'
    for filename in os.listdir('.'):
        if filename.endswith('.apk'):
            apkFilename = filename
            break

    if apkFilename:
        print 'APK: %s' % apkFilename
    else:
        print 'Failed to find APK'
    return apkFilename

def inspectApk(apkFilename):
    '''
    Inspect APK and get the package name.

    @type apkFilename: str
    @param apkFilename: The APK filename.
    @return: The application package name found in a valid APK file; or None if the APK is invalid.
    '''
    packageName = None
    tApk = execCommand('aapt dump badging %s | grep "package"' % apk, 'Inspecting APK...')
    if tApk[1]:
        packageName = re.search(r"name='(.*?)'", tApk[1]).group(1)
        versionCode = re.search(r"versionCode='(.*?)'", tApk[1]).group(1)
        versionName = re.search(r"versionName='(.*?)'", tApk[1]).group(1)
        print 'Package name: %s' % packageName    
        print 'Version name: %s' % versionName
        print 'Version code: %s' % versionCode
    else:
        print 'Failed to validate APK'
    return packageName

def findScripts():
    '''
    Scan for test scripts.

    @return: The list of test scripts; or an empty list if none is found.
    '''
    scriptFilenames = []
    print 'Scanning for test scripts...'
    if os.path.isdir(DIR_TEST_SCRIPTS):
        for filename in os.listdir(DIR_TEST_SCRIPTS):
            if filename.endswith('.py'):
                scriptFilenames.append(filename)

    if scriptFilenames:
        for i in range(0, len(scriptFilenames)):
            print 'Script %s: %s' % (i + 1, scriptFilenames[i])
    else:
        print 'No test scripts available'
    return scriptFilenames

def findDevices():
    '''
    List connected devices.

    @return: The list of device serial numbers; or an empty list if none is found.
    '''
    serialNumbers = []
    execCommand('adb devices | grep -v devices > %s/%s' % (DIR_TEST_SESSION, FILENAME_DEVICE_SERIALS), 'Listing devices...')
    serialsFile = open('%s/%s' % (DIR_TEST_SESSION, FILENAME_DEVICE_SERIALS), 'r')
    for line in serialsFile:
        match = re.search(r'([^\s]+)', line)
        if (match):
            serialNumber = match.group(0)
            serialNumbers.append(serialNumber)
            print 'Device %s: %s' % (len(serialNumbers), serialNumber)

    if (len(serialNumbers) == 0):
        print 'No devices available'
    return serialNumbers

def collectDeviceProperties(serialNumber, dirRoot):
    '''
    Collect device properties of the specified device.

    @type serialNumber: str
    @param serialNumber: The device serial number.
    @type dirRoot: str
    @param dirRoot: The root directory to put the device properties.
    '''
    execCommand('adb -s %s shell getprop > %s/%s/%s' % (serialNumber, DIR_TEST_SESSION, serialNumber, FILENAME_DEVICE_PROPERTIES), 'Collecting device properties...')
    stdoutBackup = execCommand('grep ro.product.manufacturer %s/%s; grep ro.product.model %s/%s; grep ro.build.version.sdk %s/%s' % (DIR_TEST_SESSION, FILENAME_DEVICE_PROPERTIES, DIR_TEST_SESSION, FILENAME_DEVICE_PROPERTIES, DIR_TEST_SESSION, FILENAME_DEVICE_PROPERTIES))[1]
    print stdoutBackup

def installApp(apkFilename, packageName, serialNumber):
    '''
    Install app on the specified device after uninstalling any preexisting installation.

    @type apkFilename: str
    @param apkFilename: The filename of the APK to install.
    @type packageName: str
    @param packageName: The application package name.
    @type serialNumber: str
    @param serialNumber: The serial number of the device to install the APK.
    '''
    execCommand('adb -s %s uninstall %s; adb -s %s install %s' % (serialNumber, packageName, serialNumber, apkFilename), 'Installing APK...')

def uninstallApp(packageName, serialNumber):
    '''
    Uninstall app by application package name on the specified device.

    @type packageName: str
    @param packageName: The application package name.
    @type serialNumber: str
    @param serialNumber: The serial number of the device to install the APK.
    '''
    execCommand('adb -s %s uninstall %s' % (serialNumber, packageName), 'Uninstalling application...')

def executeTestCase(packageName, serialNumber, dirRoot, scriptFilename):
    '''
    Executes a test script and performs all logging and clean-up associated with running the test case.

    @type packageName: str
    @param packageName: The application package name.
    @type serialNumber: str
    @param serialNumber: The serial number of the device to run this test case.
    @type dirRoot: str
    @param dirRoot: The root directory to put the results of this test case.
    @type scriptFilename: str
    @param scriptFilename: The test script to run.
    '''
    # Create directories to store test case results
    dirResults = '%s/%s' % (dirRoot, os.path.splitext(scriptFilename)[0])
    os.mkdir(dirResults)
    dirData = '%s/%s' % (dirResults, FOLDER_APP_DATA)
    os.mkdir(dirData)
    
    # Make a local copy of the test script
    shutil.copy('%s/%s' % (DIR_TEST_SCRIPTS, scriptFilename), dirResults)

    # Start logcat
    execCommand('adb -s %s logcat -c' % serialNumber, 'Clearing logcat buffer...')
    pLogcat = execCommand('adb -s %s logcat -v threadtime > %s/%s' % (serialNumber, dirResults, FILENAME_LOGCAT), 'Start printing logcat output to file...', wait=False)[0]

    # Execute local copy of the test script
    runTestCmd = 'python %s/%s --package %s --serial %s --root %s --logs %s --screenshots %s --screendumps %s' % (dirResults, scriptFilename, packageName, serialNumber, dirResults, FILENAME_PYUNIT, FOLDER_SCREENSHOTS, FOLDER_SCREENDUMPS)
    execCommand(runTestCmd, 'Executing [%s] with command:\n%s' % (scriptFilename, runTestCmd))

    # Stop logcat
    os.killpg(pLogcat.pid, signal.SIGTERM)
    print 'Logcat output saved'

    # Navigate to home screen and force-stop any stale backup confirmations
    execCommand('adb shell input keyevent KEYCODE_HOME')
    execCommand('adb -s %s shell am force-stop %s' % (serialNumber, PACKAGE_BACKUP_CONFIRM))

    # Send app backup request
    appDataBackup = '%s/%s' % (dirResults, FILENAME_APP_DATA_BACKUP)
    pBackup = execCommand('adb -s %s backup -f %s %s' % (serialNumber, appDataBackup, packageName), 'Downloading app data from device...', wait=False)[0]

    # Send button click to accept backup on device
    device, serialno = ViewClient.connectToDeviceOrExit(serialno=serialNumber)
    vc = ViewClient(device, serialno)
    acceptButton = vc.findViewById(ID_BUTTON_BACKUP_ACCEPT)
    if acceptButton and acceptButton.isEnabled():
        acceptButton.touch()

        # Wait for backup to complete
        pBackup.communicate()

        # Extract backed up data
        tExtract = execCommand('dd if=%s/%s bs=1 skip=24 | python -c "import zlib, sys; sys.stdout.write(zlib.decompress(sys.stdin.read()))" | tar -xvf - -C %s' % (dirResults, FILENAME_APP_DATA_BACKUP, dirData), 'Extracting app data...')
        print tExtract[1]
        print tExtract[2]

        print 'App data downloaded'
    else:
        os.killpg(pBackup.pid, signal.SIGTERM)

        # Clean up backup confirmation and corrupt backup file
        execCommand('adb -s %s shell am force-stop %s' % (serialNumber, PACKAGE_BACKUP_CONFIRM))
        if (os.path.isfile(appDataBackup)):        
            os.remove(appDataBackup)

        print 'Failed to download app data'

    # Wipe app data
    execCommand('adb -s %s shell pm clear %s' % (serialNumber, packageName), 'Wiping app data...')

#######
# Main
#######
apk = findApk()
validate(apk is not None)

package = inspectApk(apk)
validate(package is not None)

scripts = findScripts()
validate(len(scripts) > 0)

if os.path.isdir(DIR_TEST_RESULTS) is False:
    os.mkdir(DIR_TEST_RESULTS)
os.mkdir(DIR_TEST_SESSION)

serials = findDevices()
validate(len(serials) > 0)

for serial in serials:
    model = execCommand('adb -s %s shell getprop ro.product.model' % serial)[1].strip()
    dirDeviceRoot = '%s/%s-[%s]' % (DIR_TEST_SESSION, re.sub('\s+', '-', model), serial)
    os.mkdir(dirDeviceRoot)
    collectDeviceProperties(serial, dirDeviceRoot)
    installApp(apk, package, serial)
    for i in range(0, len(scripts)):
        print 'Preparing test case %s of %s [%s] on %s [%s]...' % (i + 1, len(scripts), scripts[i], serial, model)
        executeTestCase(package, serial, dirDeviceRoot, scripts[i])
    uninstallApp(package, serial)
