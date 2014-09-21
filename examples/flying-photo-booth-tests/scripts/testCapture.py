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
    sys.path.append(os.environ['ANDROID_YKSP_HOME'])
except:
    pass

from yksptestcase import YkspTestCase

TEXT_BEFORE_CAPTURE = 'PHOTO 1 OF 2'

TEXT_AFTER_CAPTURE = 'PHOTO 2 OF 2'

TEXT_AFTER_DISCARD = 'PHOTO 1 OF 2'

TEXT_CAPTURE_BUTTON = 'CAPTURE'

class CaptureTestCase(YkspTestCase):

    def testSingleCapture(self):
        '''
        Tests capturing of a single picture.
        '''
        # Start the main Activity and save the screen after one second
        self.startActivity('LaunchActivity')
        self.saveScreen('single-capture-before', sleep=1)

        # Try to find the view containing the text 'PHOTO 1 OF 2' and fail the test if unsuccessful
        try:
            self.vc.findViewWithTextOrRaise(TEXT_BEFORE_CAPTURE)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_BEFORE_CAPTURE)

        # Try to find the view containing the text 'CAPTURE' and fail the test if unsuccessful
        captureButton = None
        try:
            captureButton = self.vc.findViewWithTextOrRaise(TEXT_CAPTURE_BUTTON)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_CAPTURE_BUTTON)

        # Click on the centre of the view and save screen after five seconds
        captureButton.touch()
        self.saveScreen('single-capture-after', sleep=5)

        # Try to find the view containing the text 'PHOTO 2 OF 2' and fail the test if unsuccessful
        try:
            self.vc.findViewWithTextOrRaise(TEXT_AFTER_CAPTURE)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_AFTER_CAPTURE)

    def testSwipeDiscard(self):
        '''
        Tests the 'swipe discard' feature after capturing.
        '''
        # Start the main Activity and save the screen after one second
        self.startActivity('LaunchActivity')
        self.saveScreen('swipe-discard-before', sleep=1)

        # Try to find the view containing the text 'PHOTO 1 OF 2' and fail the test if unsuccessful
        titleView = None
        try:
            titleView = self.vc.findViewWithTextOrRaise(TEXT_BEFORE_CAPTURE)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_BEFORE_CAPTURE)

        # Try to find the view containing the text 'CAPTURE' and fail the test if unsuccessful
        captureButton = None
        try:
            captureButton = self.vc.findViewWithTextOrRaise(TEXT_CAPTURE_BUTTON)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_CAPTURE_BUTTON)

        # Get the centres of two views to be used for swipe gesture with a drag duration of 500 ms
        dragStartXY = titleView.getCenter()
        dragEndXY = captureButton.getCenter()
        dragDuration = 500

        # Click on the centre of the capture button, followed by a discard gesture after one second, then save screen after three seconds
        captureButton.touch()
        self.vc.sleep(1)
        self.device.drag(dragStartXY, dragEndXY, dragDuration)
        self.saveScreen('swipe-discard-after', sleep=3)

        # Try to find the view containing the text 'PHOTO 1 OF 2' and fail the test if unsuccessful
        try:
            self.vc.findViewWithTextOrRaise(TEXT_AFTER_DISCARD)
        except ViewNotFoundException:
            self.fail('Failed to find view with text: %s' % TEXT_AFTER_DISCARD)

if __name__ == '__main__':
    YkspTestCase.main(sys.argv)

