# Auto Input for Android

A Python application that allows you to send text input to an Android device using ADB and ADBKeyboard.

## Prerequisites

1. Python 3.x installed on your computer
2. ADB (Android Debug Bridge) installed and added to system PATH
3. ADBKeyboard.apk installed on your Android device
4. USB debugging enabled on your Android device

## Setup Instructions

1. Install ADBKeyboard on your Android device:
   - Download ADBKeyboard.apk
   - Install it on your device using: `adb install ADBKeyboard.apk`
   - Set ADBKeyboard as your default keyboard in Android settings

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Connect your Android device via USB and enable USB debugging

## Usage

1. Run the program:
   ```
   python autoInput.py
   ```

2. Type or paste your text in the input box
3. Click "Send to Android" to send the text to your device
4. The text will be automatically input wherever your cursor is on the Android device

## Features

- Supports all languages and special characters
- Simple and intuitive user interface
- Real-time connection status
- Error handling and user feedback

## Troubleshooting

If you encounter any issues:

1. Ensure ADB is properly installed and in your system PATH
2. Verify that USB debugging is enabled on your device
3. Check that ADBKeyboard is installed and set as the default keyboard
4. Make sure your device is properly connected and authorized for ADB debugging 