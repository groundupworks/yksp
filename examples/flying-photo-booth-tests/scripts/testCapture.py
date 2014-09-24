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

try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewNotFoundException

try:
    sys.path.append(os.environ['YKSP_HOME'])
except:
    pass

from yksptestcase import YkspTestCase

TEXT_CAPTURE_BUTTON = 'CAPTURE'
TEXT_BEFORE_CAPTURE = 'PHOTO 1 OF 2'
TEXT_AFTER_CAPTURE = 'PHOTO 2 OF 2'
TEXT_AFTER_DISCARD = TEXT_BEFORE_CAPTURE

class CaptureTestCase(YkspTestCase):

    def testSingleCapture(self):
        '''
        Tests capturing of a single picture.
        '''
        # Launch the app from the launcher
        self.launchApp()

        # Save the screen after one second [saveScreen() or refreshScreen() must be called to update the view tree after each screen transition]
        self.saveScreen('single-capture-before', sleep=1)

        # Find the view containing the text 'PHOTO 1 OF 2' [raise an exception to fail the test if unsuccessful]
        self.vc.findViewWithTextOrRaise(TEXT_BEFORE_CAPTURE)

        # Find the view containing the text 'CAPTURE' and click on the centre of the view
        self.vc.findViewWithTextOrRaise(TEXT_CAPTURE_BUTTON).touch()

        # Save screen after five seconds
        self.saveScreen('single-capture-after', sleep=5)

        # Find the view containing the text 'PHOTO 2 OF 2' to validate the successful capture
        self.vc.findViewWithTextOrRaise(TEXT_AFTER_CAPTURE)

    def testSwipeDiscard(self):
        '''
        Tests the 'swipe discard' feature after capturing.
        '''
        # Launch the app from the launcher
        self.launchApp()

        # Refresh the screen after one second
        self.refreshScreen(sleep=1)

        # Find the view containing the text 'PHOTO 1 OF 2'
        titleView = self.vc.findViewWithTextOrRaise(TEXT_BEFORE_CAPTURE)

        # Find the view containing the text 'CAPTURE'
        captureButton = self.vc.findViewWithTextOrRaise(TEXT_CAPTURE_BUTTON)

        # Get the centres of two views to be used for swipe gesture with a drag duration of 500 ms
        dragStartXY = titleView.getCenter()
        dragEndXY = captureButton.getCenter()
        dragDuration = 500

        # Click on the centre of the capture button, followed by a discard gesture after one second
        captureButton.touch()
        self.vc.sleep(1)
        self.device.drag(dragStartXY, dragEndXY, dragDuration)

        # Save screen after three seconds
        self.saveScreen('swipe-discard-after', sleep=3)

        # Find the view containing the text 'PHOTO 1 OF 2' to validate successful discard
        self.vc.findViewWithTextOrRaise(TEXT_AFTER_DISCARD)


if __name__ == '__main__':
    YkspTestCase.main(sys.argv)

