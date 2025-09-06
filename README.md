# Yahoo Groups Mbox to Static Website Converter

This tool converts an mbox file containing Yahoo Groups messages into a static website that can be viewed in any web browser.

## Features

- Converts mbox email archives to static HTML pages
- Preserves message threads and formatting
- Generates a clean, responsive interface
- Includes search functionality
- Maintains message metadata (date, sender, subject)

## Requirements

- Python 3.6+
- Required Python packages (install via `pip install -r requirements.txt`):
  - mailbox (standard library)
  - email (standard library)
  - jinja2
  - python-dateutil
  - markdown
  - beautifulsoup4
  - lxml

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

```
python mbox_to_website.py path/to/your/archive.mbox [output_directory]
```

### Arguments

- `archive.mbox`: Path to your Yahoo Groups mbox file
- `output_directory`: (Optional) Directory where the static site will be generated (defaults to `./output`)

## Output

The script will generate the following structure:
```
output/
├── index.html           # Main index page with all messages
├── messages/            # Individual message HTML files
│   ├── 1.html
│   ├── 2.html
│   └── ...
├── static/              # CSS and JavaScript files
│   ├── style.css
│   └── script.js
└── search/              # Search index and results
    ├── search_index.json
    └── search.html
```

## Viewing the Website

After generation, open `output/index.html` in any web browser to view the archive.