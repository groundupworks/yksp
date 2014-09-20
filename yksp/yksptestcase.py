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

    dirScreens = None

    screenCount = 0

    def setUp(self):
        self.device, self.serialno = ViewClient.connectToDeviceOrExit(serialno=YkspTestCase.serial)
        self.vc = ViewClient(self.device, self.serialno)

    def tearDown(self):
        self.device.shell('am force-stop %s' % YkspTestCase.package)

    def startActivity(self, activity):
        self.device.startActivity('%s/.%s' % (YkspTestCase.package, activity))

    def screenshot(self, tag=None):
        toFile = None
        if tag:
            toFile = '%s/%s-%s.png' % (YkspTestCase.dirScreens, YkspTestCase.screenCount, tag)
        else:
            toFile = '%s/%s.png' % (YkspTestCase.dirScreens, YkspTestCase.screenCount)
        self.device.takeSnapshot(reconnect=True).save(toFile, 'PNG')
        YkspTestCase.screenCount += 1

    @staticmethod
    def parseArgs(argv):
        package = None
        serial = None
        dirScreens = None

        try:
            opts, args = getopt.getopt(argv[1:], 'hp:s:d:', ['help', 'package=', 'serial=', 'screens='])
        except getopt.GetoptError:
            YkspTestCase.usage(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                YkspTestCase.usage(2)
            elif opt in ('-p', '--package'):
                package = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-s', '--serialno'):
                serial = arg
                argv.remove(opt)
                argv.remove(arg)
            elif opt in ('-d', '--screens'):
                dirScreens = arg
                argv.remove(opt)
                argv.remove(arg)

        if package is None:
            print '\nError:'
            print '--package must be specified'
            YkspTestCase.usage(2)
        if serial is None:
            print '\nError:'
            print '--serial must be specified'
            YkspTestCase.usage(2)
        if dirScreens is None:
            print '\nError:'
            print '--screens must be specified'
            YkspTestCase.usage(2)
        if os.path.isdir(dirScreens) is False:
            print '\nError:'
            print '--screens specifies an invalid directory'
            YkspTestCase.usage(2)

        return package, serial, dirScreens

    @staticmethod
    def usage(exitVal=0):
        print '\nUsage:'
        print '-h, --help                 OPTIONAL    print this help and exit'
        print '-p, --package <package>    REQUIRED    specify the package name of the application'
        print '-s, --serial <serial>      REQUIRED    specify serial number of the device to run this test case'
        print '-d, --screens <dir>        REQUIRED    specify existing directory to store screenshots'
        sys.exit(exitVal)

    @staticmethod
    def main(argv):
        YkspTestCase.package, YkspTestCase.serial, YkspTestCase.dirScreens = YkspTestCase.parseArgs(argv)
        unittest.main()


if __name__ == '__main__':
    YkspTestCase.main(sys.argv)
