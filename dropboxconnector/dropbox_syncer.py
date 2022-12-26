import sys
import dropbox
import os
import logging
from dotenv import dotenv_values
from flask import jsonify

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def create_client(auth_token):
    """
    Validates access token and generates a client
    Returns:
        dbx_client: Client to make api requests to Dropbox API
    """
    access_token = auth_token
    # Create a Dropbox API client using the access token
    dbx_client = dropbox.Dropbox(access_token)

    # Validate the access token by making a test API call
    try:
        dbx_client.users_get_current_account()
        logging.info("Dropbox access token is valid")
    except dropbox.exceptions.AuthError:
        logging.critical("Error: Invalid Dropbox access token")
        sys.exit(10)

    return dbx_client


def sync_files_from_dropbox(local_path, dropbox_client, dropbox_path=""):
    """One way sync to download all files from dropbox folder to local dir.
    Only fetches files which are missing/out of date in local path.

    Args:
        local_path (str): Path in local system to store downloaded files.
        dropbox_client (object): Client to access dropbox apis
        dropbox_path (str, optional): Path to folder in dropbox. Defaults to "" which is root.
    """

    # Fetch the files in the Dropbox directory
    results = dropbox_client.files_list_folder(dropbox_path)

    # List of synced files
    synced_files = []

    # Iterate through the list of entries and download each file or folder to the local directory
    for entry in results.entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            # Download the file
            file_path = entry.path_display
            local_file_path = os.path.join(local_path, entry.name)
            # If file doesn't exist or has been updated download
            if (
                    not os.path.exists(local_file_path)
                    or os.path.getmtime(local_file_path) < entry.client_modified.timestamp()
            ):
                # Download the file
                md, res = dropbox_client.files_download(file_path)
                synced_files.append(entry.name)
                logging.info("Downloading file %s", entry.name)
                file_content = res.content
                # Save the file to the local directory
                with open(local_file_path, "wb") as f:
                    f.write(file_content)

        elif isinstance(entry, dropbox.files.FolderMetadata):
            # Download the sub folder (recursive function call)
            sync_files_from_dropbox(local_path, dropbox_client, entry.path_display)

    logging.info("Synchronization complete")
    return jsonify(synced_files)
