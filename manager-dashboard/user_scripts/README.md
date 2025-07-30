## Description
This read me will guide you on how to create a COCO file using the utility script for Google Drive and DropBox

## Google Drive
You can find the utility script for Google Drive here: [generate_coco_from_drive.js](./generate_coco_from_drive.js)

### Prerequisites
- You must have a Google account
- Your image files should be stored in a public Google Drive folder
- You have access to Google Apps Script via https://script.google.com

### Creation Steps
- Create a Google Apps script project
    - Go to https://script.google.com
    - Click on "New Project"
    - Rename the project name to your desired project name
- Paste the utility script
    - Replace any existing default code the code from this utility file
- Replace Placeholder Values
    - Replace `your_coco_export.json` with your output filename
    - Replace `your_public_folder_id` with the ID of your Google Drive folder
> The folder ID is the alphanumeric string that appears after "/folders/" in the URL.\
> Eg: drive.google.com/drive/folders/**1prcCevijN5mubTllB2kr5ki1gjh_IO4u**?usp=sharing
- Run the script
    - Save the project to Drive using the floppy disk 💾 icon
    - Press Run
    - Accept the authorization prompts the first time you run the script
- View COCO JSON Output
    - Go to View > Logs
    - Copy the Google Drive URL where the coco file is created and generated
    - Download the json file

## DropBox
You can find the utility script for DropBox here: [generate_coco_from_dropbox.py](./generate_coco_from_dropbox.py)

### Prerequisites
- Create account: https://www.dropbox.com/register
- Create new App: https://www.dropbox.com/developers/apps
    - Choose an API: Scoped access
    - Choose the type of access you need: Full Dropbox
    - Name your app: `your-app-name`
- Update `Permission type`
    - Go to the app settings
    - Click **Scoped App**
    - Tick the following
        - files.metadata.read
        - files.content.write
        - files.content.read
        - sharing.write
        - sharing.read
    - Submit
- Generate new access token:
    - Go to the app settings
    - Click **Generated access token**
- Install uv on your system: https://docs.astral.sh/uv/getting-started/installation/
- Download the [generate_coco_from_dropbox.py](./generate_coco_from_dropbox.py) script
- Create a DropBox folder and upload images
  - Your image files should be stored in a public DropBox folder

### Creation Steps
- Copy the folder pathname in DropBox
- Copy the generated access token from DropBox
- Run the script
```bash
    # Help
    uv run generate_coco_dropbox.py --help
    
    # Sample
    uv run generate_coco_dropbox.py "DROPBOX_ACCESS_TOKEN" "FOLDER_PATHNAME_IN_DROPBOX" "DESTINATION_EXPORT_FILE_NAME_IN_DROPBOX"
    
    # Example
    uv run generate_coco_dropbox.py sl.yourAccessTokenHere “/COCO TEST” “coco_export.json”
```
- Download the exported coco json from the link in terminal or your DropBox folder
