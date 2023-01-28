import os

import dropbox
import gdshortener
from colorama import Fore, Style
from dropbox.files import WriteMode

from console import put


class Storage:
    """Class for storing and loading of data in the cloud
    """

    REMOTE_PATH = "/lists.json"

    def __init__(self):
        """Constructor method, authenticates the user with Dropbox
        """
        # Adapted from example code at:
        # https://github.com/dropbox/dropbox-sdk-python/blob/main/example/oauth/commandline-oauth-pkce.py
        key = os.environ['APP_KEY']
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
            key, use_pkce=True, token_access_type='offline')
        authorize_url = auth_flow.start()

        # Shorten the URL for easier copypaste from console
        shortener = gdshortener.ISGDShortener()
        short_url = shortener.shorten(authorize_url)[0]

        put("=== DROPBOX WIZARD ===\n")
        put("\n")
        put("To authenticate with Dropbox, please open this URL in your ")
        put("web browser: \n")
        put("\n")
        put(f"{Fore.LIGHTGREEN_EX}{short_url}{Style.RESET_ALL}\n")
        put("\n")
        put("(The link has been shortened for convenience, and should lead\n")
        put("to a URL beginning with ")
        put("\"https://www.dropbox.com/oauth2/authorize\".\n")
        put("If the link matches this pattern, proceed past the is.gd ")
        put("warning page.)\n")
        put("\n")
        put("On the page, log in to Dropbox if needed, and click \"Allow\".\n")
        put("Once you receive the authorization code, please paste it below:\n")
        put("> ")
        auth_code = input().strip()

        try:
            oauth_result = auth_flow.finish(auth_code)
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Dropbox: {e}")

        self._dbx = dropbox.Dropbox(
            oauth2_refresh_token=oauth_result.refresh_token, app_key=key)

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
