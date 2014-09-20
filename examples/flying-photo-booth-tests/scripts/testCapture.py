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
import unittest

try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewNotFoundException

try:
    sys.path.append(os.environ['ANDROID_YKSP'])
except:
    pass

from yksptestcase import YkspTestCase

TEXT_BEFORE_CAPTURE = 'PHOTO 1 OF 2'

TEXT_AFTER_CAPTURE = 'PHOTO 2 OF 2'

TEXT_CAPTURE_BUTTON = 'CAPTURE'

class CaptureTestCase(YkspTestCase):

    def testCapture(self):
        self.startActivity('LaunchActivity')
        self.vc.dump(window=-1)
        self.screenshot('before-capture')

        try:
            self.vc.findViewWithTextOrRaise(TEXT_BEFORE_CAPTURE)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_BEFORE_CAPTURE)

        captureButton = None
        try:
            captureButton = self.vc.findViewWithTextOrRaise(TEXT_CAPTURE_BUTTON)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_CAPTURE_BUTTON)

        captureButton.touch()

        self.vc.sleep(3)
        self.vc.dump(window=-1)
        self.screenshot('after-capture')

        try:
            self.vc.findViewWithTextOrRaise(TEXT_AFTER_CAPTURE)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_AFTER_CAPTURE)


if __name__ == '__main__':
    YkspTestCase.main(sys.argv)
