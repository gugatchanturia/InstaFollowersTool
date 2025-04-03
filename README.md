# Instagram Followers Analysis Tool

This tool analyzes your Instagram followers and following to find users who don't follow you back. It uses Instagram's mobile API for reliable data collection and your existing Chrome profile for authentication.

## Features

- Uses Instagram's mobile API for faster and more reliable data collection
- Gets exact counts of followers and following
- Uses your existing Chrome profile for authentication (no need to log in)
- Identifies users who don't follow you back
- Handles large lists efficiently

## Requirements

- Python 3.6 or higher
- Chrome browser
- Must be logged into Instagram in Chrome

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/gugatchanturia/InstaFollowersTool.git
   cd InstaFollowersTool
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Open `tool.py` and change the Chrome profile path to your username:
   ```python
   options.add_argument("user-data-dir=C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Google\\Chrome\\User Data")
   ```

## Usage

1. Make sure you're logged into Instagram in Chrome
2. Run the script:
   ```bash
   python tool.py
   ```
3. Enter the Instagram username you want to analyze
4. Wait for the results

## Notes

- The tool will only work if you're logged into Instagram in Chrome
- You can only see followers and following of private accounts if you are authorized
- If authorized, you can see this information for accounts you are connected with (those who follow you or whom you follow back)
- The tool will work for private accounts only if you have the necessary permissions
- The count shown on Instagram's website might be different from the actual number of accessible accounts due to:
  - Blocked accounts (they are counted but not accessible)
  - Disabled accounts (they are counted but not accessible)
  - Accounts that have blocked you (they are counted but not accessible)
- If the script shows a different count than Instagram's website, this is likely due to the above reasons

## Troubleshooting

If you encounter any issues:

1. Make sure you're logged into Instagram in Chrome
2. Try closing all Chrome windows and running the script again
3. If the script stops before collecting all followers or following, try running it again
4. If the count is different from Instagram's website, this is normal due to blocked/disabled accounts
5. If you get authentication errors, make sure you're logged into Instagram in Chrome

## License

This project is licensed under the MIT License - see the LICENSE file for details. 