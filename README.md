yksp
====

A fully Python-based tool that helps you automate Android UI testing and captures everything you need from each test session.

* Generation of UI events independent of device screen sizes
* Validation of UI elements with PyUnit assertions
* Screenshots and dumps of their matching view tree
* Logcat output for the duration of each test
* App data dump after each test, including preferences and databases
* Backup file that can be used to restore your device state from each test
* Execution of tests on all connected devices in parallel
* Device properties dump, including the device model and installed Android version

You can see yksp in action [here](https://www.facebook.com/video.php?v=688024157960505). Higher abstractions of UI interactions used to compose test scripts are available through [AndroidViewClient](https://github.com/dtmilano/AndroidViewClient) by @dtmilano. This project will focus on tools to inspect, correlate, and validate the set of generated test results. Pull requests are, of course, welcome.

Refer to the [Project Site](http://benhylau.github.io/yksp) to get started.
