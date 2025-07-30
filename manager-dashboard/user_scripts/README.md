## DropBox
### Prerequisites

- Create account: https://www.dropbox.com/register
- Create new App: https://www.dropbox.com/developers/apps
    - Choose an API: Scoped access
    - Choose the type of access you need: Full Dropbox
    - Name your app: Mapswipe COCO
- Update `Permission type`
    - Go to the app settings
    - Click **Scoped App**
    - Select
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
- Download the [generate_coco_from_dropbox.py](user_scripts/generate_coco_from_dropbox.py) script
- Run the script
    ```bash
    # Help
    uv run generate_coco_dropbox.py --help

    # Sample
    uv run generate_coco_dropbox.py "DROPBOX_ACCESS_TOKEN" "FOLDER_PATH_IN_DROPBOX" "DESTINATION_EXPORT_FILE_NAME_IN_DROPBOX"

    # Example
    uv run generate_coco_dropbox.py sl.yourAccessTokenHere “/COCO TEST” “coco_export.json”
    ```
- Download the coco_export.json from the dropbox
