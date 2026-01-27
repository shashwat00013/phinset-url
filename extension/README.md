# Phishing Detector Chrome Extension

## Installation

1. **Start the Flask server first:**
   ```bash
   cd e:\phising
   python app.py
   ```

2. **Load the extension in Chrome:**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (top right toggle)
   - Click "Load unpacked"
   - Select the `e:\phising\extension` folder

## Features

- **Popup Interface**: Click the extension icon to analyze any URL
- **Auto-Check**: Automatically checks pages when you visit them
- **Real-time Warnings**: Shows alerts for suspicious/unsafe websites
- **Detailed Analysis**: Displays ML probability and rule adjustments

## Usage

1. The Flask server must be running on `http://localhost:5000`
2. Click the extension icon to check the current URL
3. Browse normally - the extension will warn you about dangerous sites
4. Warnings can be dismissed and auto-hide after 10 seconds

## Files

- `manifest.json` - Extension configuration
- `popup.html/js` - Extension popup interface
- `content.js` - Real-time page checking
- Icons (16x16, 48x48, 128x128) - Extension icons (add your own)

## Notes

- Requires the Flask phishing detector to be running
- Works with HTTP and HTTPS sites
- Uses the same ML model as the web application
