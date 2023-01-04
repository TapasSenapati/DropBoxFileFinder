import logging
import os

import dropbox
from flask import jsonify

from dropbox_finder.clientutils.client_helpers import (
    get_dropbox_client,
    get_rabbitmq_connection,
    get_redis_connection,
)
from dropbox_finder.producer.mq_producer import add_message_for_processing

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def update_message_queue(account):
    """Call /files/list_folder for the given user ID and put change metadata(name of file,time modified, change type)
    Args:
        account (str): DropBox account id
    """

    # Get redis ,rabbitmq and dropbox connections
    redis_connection = get_redis_connection(0)
    mq_connection = get_rabbitmq_connection()

    # OAuth token for the user
    token = redis_connection.hget("tokens", account)
    logging.info("auth token fetched %s", token)

    # cursor for the user (None the first time)
    cursor = redis_connection.hget("cursors", account)

    dbx = get_dropbox_client(token)
    has_more = True

    try:
        while has_more:
            if cursor is None:
                result = dbx.files_list_folder(path="")
            else:
                result = dbx.files_list_folder_continue(cursor)

            for entry in result.entries:
                logging.info("Iterating file %s", entry.name)
                change_data = {}
                # Name of modified file
                change_data["file_path"] = entry.path_lower
                change_data["file_name"] = entry.name

                # we are ignoring folder changes at this point of time
                if isinstance(entry, dropbox.files.FolderMetadata):
                    continue
                
                if isinstance(entry, dropbox.files.DeletedMetadata):
                    change_data["change_type"] = "delete"
                else:
                    # we have file meta data.update here could mean adding a new file or modifying an existing file in dropbox
                    change_data["change_type"] = "update"
                    # File size in bytes
                    change_data["file_size"] = entry.size
                
                add_message_for_processing(mq_connection, change_data)

            # Update cursor
            cursor = result.cursor
            redis_connection.hset("cursors", account, cursor)

            # Repeat only if there's more to do
            has_more = result.has_more
    finally:
        # Close the connections
        redis_connection.close()
        dbx.close()
        mq_connection.close()
