import os

import dropbox
from dropbox.files import WriteMode


class Storage:
    """Class for storing and loading of data in the cloud
    """

    REMOTE_PATH = "/lists.json"

    def __init__(self):
        """Constructor method
        """
        token = os.environ['TOKEN']
        self._dbx = dropbox.Dropbox(token)

    def download(self):
        """Retrieve data from storage, and return as text

        :return: Data downloaded from online storage
        :rtype: str
        :raises RuntimeError: Any failure to upload the data
        """
        try:
            _, response = self._dbx.files_download(self.REMOTE_PATH)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Failed to download data from Dropbox: {e}")

    def upload(self, text_data):
        """Store data in the storage, replacing previous data

        :param text_data: Data to store as UTF-8 plaintext
        :type text_data: str
        :raises RuntimeError: Any failure to upload the data
        """
        try:
            self._dbx.files_upload(text_data.encode(), self.REMOTE_PATH,
                                   WriteMode.overwrite)
        except Exception as e:
            raise RuntimeError(f"Failed to upload data to Dropbox: {e}")
