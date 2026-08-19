CLOCK PRO MINIMAL CUSTOM - FIXED
=================================

The previous version had this error:

    TypeError: argument 1 has unexpected type 'QPushButton'

CAUSE:
The close button was accidentally named "self.close". QWidget already has
a close() method, so this replaced the method with a QPushButton.

FIX:
The button is now named "self.close_btn" and calls "self.close_app()".

FEATURES:
- Minimal clock matching the requested design
- Drag anywhere when unlocked
- Lock / unlock position
- Always-on-top toggle
- 12-hour / 24-hour format
- Show/hide seconds
- Show/hide date
- Choose time font
- Choose time font size
- Choose date font
- Choose date font size
- Choose time color
- Choose date color
- Choose background color
- Transparency
- Widget width and height
- Remembers position and settings

RUN:
Double-click run.bat

BUILD:
Double-click build.bat

Then run:
dist\ClockPro.exe
