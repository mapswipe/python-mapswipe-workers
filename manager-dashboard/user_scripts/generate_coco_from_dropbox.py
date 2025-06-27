# /// script
# dependencies = [
#   "requests<3",
# ]
# ///
from pathlib import Path
from argparse import ArgumentParser
import requests
import json
import re

def dropbox_request(endpoint: str, data: object, *, access_token: str):
    url = f"https://api.dropboxapi.com/2/{endpoint}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    res = requests.post(
        url,
        headers=headers,
        data=json.dumps(data),
    )
    res.raise_for_status()
    return res.json()

def dropbox_content_request(endpoint: str, path: str, data: object, *, access_token: str):
    url = f"https://content.dropboxapi.com/2/{endpoint}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": path,
            "mode": "overwrite",   # overwrite if exists
            "autorename": False,
            "mute": False
        })
    }
    res = requests.post(
        url,
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
    )
    res.raise_for_status()
    return res.json()

def list_all_files(folder_path: str, *, access_token: str):
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    files = []

    data = {"path": folder_path, "recursive": False}
    response = dropbox_request("files/list_folder", data, access_token=access_token)

    files.extend(response.get("entries", []))

    while response.get("has_more", False):
        cursor = response["cursor"]
        response = dropbox_request(
            "files/list_folder/continue",
            {"cursor": cursor},
            access_token=access_token,
        )
        files.extend(response.get("entries", []))

    # Sort files by name (just in case)
    files = sorted(files, key=lambda file: file["name"].lower())
    # Filter out only files (not folders) that are supported
    files = [
        file for file in files
        if file[".tag"] == "file" and Path(file["name"]).suffix.lower() in ALLOWED_EXTENSIONS
    ]
    return files

def share_file_and_get_links(files, *, access_token: str):
    total = len(files)
    images = []
    for i, file in enumerate(files):
        path = file["path_lower"]
        actual_path = file["path_display"]

        # First try to list existing shared links
        data = {"path": path, "direct_only": True}
        print(f"{i + 1}/{total} Getting public URL")
        res = dropbox_request(
            "sharing/list_shared_links",
            data,
            access_token=access_token,
        )
        if res.get("links"):
            link = res["links"][0]["url"]
        else:
            data = {
                "path": path,
                "settings": {
                    "requested_visibility": "public"
                }
            }
            res_create = dropbox_request(
                "sharing/create_shared_link_with_settings",
                data,
                access_token=access_token,
            )
            link = res_create["url"]

        raw_url = re.sub(r'&dl=0\b', '', link) + '&raw=1'

        images.append({
            "id": i + 1,
            "file_name": actual_path,
            "coco_url": raw_url,
        })
    return images


def main():
    parser = ArgumentParser(description="Generate COCO file from images folder.")
    parser.add_argument("access_token", help="Access token for authentication")
    parser.add_argument("images_folder", help="Path to the images folder")
    parser.add_argument("export_file_name", help="Name of the export COCO file")

    args = parser.parse_args()

    access_token = args.access_token
    images_folder = args.images_folder
    export_file_name = args.export_file_name

    # Get all the files on given path
    files = list_all_files(
        images_folder,
        access_token=access_token,
    )

    # Share individual file publically and get public link
    public_images = share_file_and_get_links(
        files,
        access_token=access_token,
    )

    # Upload coco format export to dropbox
    print("Uploading COCO file")
    absolute_export_file_name = str(Path(images_folder) / Path(export_file_name))
    dropbox_content_request(
        "files/upload",
        absolute_export_file_name,
        { "images": public_images },
        access_token=access_token,
    )

    # Get temporary link
    res = dropbox_request(
        "files/get_temporary_link",
        { "path": absolute_export_file_name },
        access_token=access_token,
    )
    print(f"COCO file available at {res["link"]}")

if __name__ == "__main__":
    main()
