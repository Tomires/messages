# Facebook message analyser

This script does rather peculiar stuff with your private data. Enjoy!

## Prerequisites
This script requires the following packages:

| Package    | Website                                 |
|------------|-----------------------------------------|
| numpy      | https://pypi.python.org/pypi/numpy      |
| pandas     | https://pypi.python.org/pypi/pandas     |
| matplotlib | https://pypi.python.org/pypi/matplotlib |

## Data preparation
1. Download a copy of your Facebook data from https://www.facebook.com/settings
2. Convert messages.html to json using https://github.com/ownaginatious/fbchat-archive-parser
3. Paste the resulting **messages.json** file to the */data* folder
4. Create a **names.csv** file in the */data* folder containing pairings of Facebook e-mail identifiers with human-readable nicknames using the following example as reference.

```
1234567890@facebook.com,John Doe
0987654321@facebook.com,Joe Barett
```
