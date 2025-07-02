# QS-Tools - Character Analysis Tool

A web application for analyzing text and CSV files for special characters. This tool helps identify characters that would be modified by PHP normalization functions, including specific symbols, HTML sensitive characters, and non-ASCII characters.

## Features

- Upload and analyze text (.txt) or CSV (.csv) files
- Detect special characters including specific symbols, HTML sensitive characters, and non-ASCII characters
- Automatic detection of file encodings (UTF-8, Windows-1252, Latin-1, etc.)
- Detailed report with character counts and locations
- Simple and responsive web interface

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the web server:
   ```
   python app.py
   ```
2. Open your browser and navigate to http://127.0.0.1:5000
3. Upload a text or CSV file
4. Click "Analyze File" to view the results (file encoding will be detected automatically)

## Command Line Usage

You can still use the legacy command line tool:

```
python legacy.py your_file.txt [-e encoding]
```

Where:
- `your_file.txt` is the path to the file you want to analyze
- `-e` or `--encoding` specifies the file encoding (default is UTF-8)