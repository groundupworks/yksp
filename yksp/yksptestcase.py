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
import getopt
import unittest

try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewClient

class YkspTestCase(unittest.TestCase):

    package = None

    serial = None

    dirRoot = None

    logsFilename = None

    screenshotFolder = None

    screendumpFolder = None

    screenCount = 0

    def setUp(self):
        # Connnect to device
        self.device, self.serialno = ViewClient.connectToDeviceOrExit(serialno=YkspTestCase.serial)

        # Wake device
        self.device.wake()

        # Create ViewClient instance
        self.vc = ViewClient(self.device, self.serialno)

    def tearDown(self):
        # Force-stop the app
        self.device.shell('am force-stop %s' % YkspTestCase.package)

    def startActivity(self, activity, package=None):
        '''
        Starts an Activity.

        @type activity: str
        @param activity: The name of the Android Activity.
        @type package: str
        @param package: An optional parameter to indicate the package name of the Activity. If not provided, the application package name specified in the application manifest is used.
        '''
        if package is None:
            package = YkspTestCase.package
        self.device.startActivity('%s/.%s' % (package, activity))

    def saveScreen(self, tag=None, sleep=0):
        '''
        Saves to disk the screenshot and screendump of the device screen.

        @type tag: str
        @param tag: The tag for this screen. This is appended to the filenames.
        @type sleep: float
        @param sleep: An optional parameter to indicate the time to sleep before saving the screen. Defaults to zero.
        '''
        if sleep > 0:
            self.vc.sleep(sleep)

        filename = YkspTestCase.screenCount
        if tag:
            filename = '%s-%s' % (filename, tag)

        # Take a screenshot and save
        self.device.takeSnapshot(reconnect=True).save('%s/%s/%s.png' % (YkspTestCase.dirRoot, YkspTestCase.screenshotFolder, filename), 'PNG')

        # Take a screendump and save
        screendump = self.vc.dump(window=-1, sleep=0)
        screendumpStream = open('%s/%s/%s.txt' % (YkspTestCase.dirRoot, YkspTestCase.screendumpFolder, filename), 'w')
        self.vc.traverse(transform=self.vc.TRAVERSE_CITPS, stream=screendumpStream)
        screendumpStream.close()

        YkspTestCase.screenCount += 1

    @staticmethod
    def parseArgs(argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hp:s:r:l:m:n:', ['help', 'package=', 'serial=', 'root=', 'logs=', 'screenshots=', 'screendumps='])
        except getopt.GetoptError:
            YkspTestCase.usage(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                YkspTestCase.usage(2)
            elif opt in ('-p', '--package'):
                YkspTestCase.package = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-s', '--serial'):
                YkspTestCase.serial = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-r', '--root'):
                YkspTestCase.dirRoot = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-l', '--logs'):
                YkspTestCase.logsFilename = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-m', '--screenshots'):
                YkspTestCase.screenshotFolder = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-n', '--screendumps'):
                YkspTestCase.screendumpFolder = arg
                argv.remove(opt)
                argv.remove(arg)

        if YkspTestCase.package is None:
            print '\nError:'
            print '--package must be specified'
            YkspTestCase.usage(2)
        if YkspTestCase.serial is None:
            print '\nError:'
            print '--serial must be specified'
            YkspTestCase.usage(2)
        if YkspTestCase.dirRoot is None:
            print '\nError:'
            print '--root must be specified'
            YkspTestCase.usage(2)
        if YkspTestCase.screenshotFolder is None:
            print '\nError:'
            print '--screenshots must be specified'
            YkspTestCase.usage(2)
        if YkspTestCase.screendumpFolder is None:
            print '\nError:'
            print '--screendumps must be specified'
            YkspTestCase.usage(2)
        if os.path.isdir(YkspTestCase.dirRoot) is False:
            print '\nError:'
            print '--root specifies an invalid directory'
            YkspTestCase.usage(2)

    @staticmethod
    def usage(exitVal=0):
        print '\nUsage:'
        print '-h, --help                    OPTIONAL    print this help and exit'
        print '-p, --package <package>       REQUIRED    specify the package name of the application'
        print '-s, --serial <serial>         REQUIRED    specify the serial number of the device to run this test case'
        print '-r, --root <dir>              REQUIRED    specify the root directory to save the results of this test case'
        print '-l, --logs <dir>              OPTIONAL    specify the filename to save the PyUnit logs'
        print '-m, --screenshots <folder>    REQUIRED    specify the folder name to save the screenshots'
        print '-n, --screendumps <folder>    REQUIRED    specify the folder name to save the screendumps'
        sys.exit(exitVal)

    @staticmethod
    def main(argv):
        YkspTestCase.parseArgs(argv)

        # Create subdirectories
        dirScreenshot = '%s/%s' % (YkspTestCase.dirRoot, YkspTestCase.screenshotFolder)
        if os.path.isdir(dirScreenshot) is False:
            os.mkdir(dirScreenshot)
        dirScreendump = '%s/%s' % (YkspTestCase.dirRoot, YkspTestCase.screendumpFolder)
        if os.path.isdir(dirScreendump) is False:
            os.mkdir(dirScreendump)

        # Configure logging and execute test case
        if YkspTestCase.logsFilename:
            logsStream = open('%s/%s' % (YkspTestCase.dirRoot, YkspTestCase.logsFilename), 'w')
            runner = unittest.TextTestRunner(stream=logsStream, verbosity=2)
            unittest.main(testRunner=runner)
        else:
            unittest.main()


if __name__ == '__main__':
    YkspTestCase.main(sys.argv)

