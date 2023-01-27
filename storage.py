import os

import dropbox
from dropbox.files import WriteMode


class Storage:
    """Class for storing and loading of data in the cloud
    """

    def __init__(self):
        """Constructor method
        """
        token = os.environ['TOKEN']
        self._dbx = dropbox.Dropbox(token)

    def upload(self, text_data):
        """Store data in the storage, replacing previous data

        :param text_data: Data to store as UTF-8 plaintext
        :type text_data: str
        :raises RuntimeError: Any failure to upload the data
        """
        try:
            self._dbx.files_upload(text_data.encode(), "/lists.json", WriteMode.overwrite)
        except Exception as e:
            raise RuntimeError(f"Failed to upload data to Dropbox: {e}")
