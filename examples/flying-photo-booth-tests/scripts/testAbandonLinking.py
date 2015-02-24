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
    sys.path.append(os.environ['YKSP_HOME'])
except:
    pass

from yksptestcase import YkspTestCase

# The unique ID of the Preferences button is identified using the 'dump' tool
ID_BUTTON_PREFERENCES = 'com.groundupworks.flyingphotobooth:id/preferences_button'

TEXT_PREFERENCES = 'Preferences'
TEXT_ARRANGEMENT = 'Arrangement'
TEXT_LINK = 'Enable one-click or auto share'

NUM_LINKABLE_SERVICES = 3

PACKAGE_FACEBOOK = 'com.facebook.katana'
PACKAGE_DROPBOX = 'com.dropbox.android'

class AbandonLinkingTest(YkspTestCase):

    def preconditions(self):
        '''
        Tests for preconditions.
        '''
        # Check for Facebook and Dropbox app installions by ensuring their paths do not return empty
        if self.device.shell('pm path %s' % PACKAGE_FACEBOOK): pass
        else: self.fail('Precondition not met. Required package %s is not installed on this device' % PACKAGE_FACEBOOK)
        if self.device.shell('pm path %s' % PACKAGE_DROPBOX): pass
        else: self.fail('Precondition not met. Required package %s is not installed on this device' % PACKAGE_DROPBOX)

    def testAbandonLinking(self):
        '''
        Tests the proper handling of the user abandoning the Facebook and Dropbox linking process by pressing the BACK key.
        '''
        # Verify preconditions
        self.preconditions()

        # Launch the app from the launcher
        self.launchApp()

        # Refresh the screen after one second [saveScreen() or refreshScreen() must be called to update the view tree after each screen transition]
        self.refreshScreen(sleep=1)

        # Find the Preferences button by ID and click on the centre of the view [raise an exception to fail the test if unsuccessful]
        self.vc.findViewByIdOrRaise(ID_BUTTON_PREFERENCES).touch()

        # Save screen after one second
        self.saveScreen('preferences', sleep=1)

        # Get the centres of two views and scroll with a drag duration of 500 ms
        dragStartXY = self.vc.findViewWithTextOrRaise(TEXT_LINK).getCenter()
        dragEndXY = self.vc.findViewWithTextOrRaise(TEXT_ARRANGEMENT).getCenter()
        self.device.drag(dragStartXY, dragEndXY, 500)

        # Save screen with no delay
        self.saveScreen('preferences-scrolled', sleep=0)

        # Find the list of views containing the 'Enable one-click or auto share' text
        linkViews = []
        allViews = self.vc.dump(sleep=0)
        for view in allViews:
            if view.getText() == TEXT_LINK:
                linkViews.append(view)
        
        # Assert that NUM_LINKABLE_SERVICES linkable services are found
        self.assertEqual(len(linkViews), NUM_LINKABLE_SERVICES, 'Found only %s linkable services, expected %s' % (len(linkViews), NUM_LINKABLE_SERVICES))

        # Iterate over list of link views
        i = 0
        for view in linkViews:
            # Click on the centre of the view and save screen after one second [long wait for network call]
            view.touch()
            self.saveScreen('service-%s' % i, sleep=5)

            # Click the BACK key to abandon and save screen after 0.5 second [short wait to capture toast]
            self.device.press('KEYCODE_BACK')
            self.saveScreen('abandon-linking-%s' % i, sleep=0.5)
            i += 1

            # Assert that we are back at the Preferences screen
            self.vc.findViewWithTextOrRaise(TEXT_PREFERENCES)


if __name__ == '__main__':
    YkspTestCase.main(sys.argv)

