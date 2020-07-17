# Text File Bookmarks / Startpage

1. Simple text-file-based, hierarchical bookmark management system
2. Exports to a custom browser "start page" with auto-completion for bookmark titles and domains
3. Supports export of Chromium-family or Safari browser bookmarks
4. Can fully replace browser start pages without requiring 3rd party extension software installation (a security risk)

Demo Startpage (also contained in the example/ folder):
[https://petergriff.in/bookmark_startpage_demo/startpage.html](https://petergriff.in/bookmark_startpage_demo/startpage.html)


### Bookmark Format:

Files ending in .txt, containing a newlines-separated list of bookmarks in the format of:
```
<bookmark title>
<bookmark URL>
<optional note>
```

Root directory file 'startpage.columns' defines the ordering of 'folders' in the startpage


### Startpage Creation Usage

render_startpage [-h] [-d] [-v] [--dry-run] source-directory output-directory

Writes the HTML file and handles the static files that create a start page
from the standard bookmarks textfiles.

positional arguments:
  source-directory      Directory containing bookmarks text files.
  output-directory      Output directory for generated start page.

optional arguments:
  -h, --help            show this help message and exit
  -d, --download-favicons
                        Optionally attempt to download favicons.
  -v, --verbosity       Increases verbosity, sets logging to DEBUG.
  --dry-run             Reads and processess site, skips writing files.

Program overrwites files each run.



### Google New Tab shortcut override in Mac OSX 10.12.6

Removes need to install a 3rd party browser extension to change the page opened when a new tab is opened (!!!)

###### Automator application
1. File dropdown menu
2. choose 'New'
3. choose 'Service'
4. Library / Utilities / Run Shell Script (double click to add)
5. past in the shell command: ```open -a "Google Chrome" file:///<PATH>/startpage/startpage.html```
6. Save, name it something unique like 'Custom Chrome New Tab Page'


###### System Preferences / Security and Privacy
1. Privacy Tab (far right along the top)
2. Accessibility (in list on the left)
3. Open lock on bottom-left as admin to allow changes
4. Add the 'Automator' to the list of 'Allow the apps below to control your computer'


###### System Preferences / Keyboard
1. Shortcuts Tab (middle of the top)
2. Services (in the list on the left)
3. Assign a keyboard shortcut of CMD-T to 'Custom Chrome New Tab Page'
4. Navigate to App Shortcuts (in the same list as services)
5. Press '+' button, choose Google Chrome
6. Set 'Menu Title' as 'New Tab'
7. Give it some other keyboard shortcut (like Option-CMD-T)

