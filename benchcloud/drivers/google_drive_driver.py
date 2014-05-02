import httplib2
import pprint
from mimetypes import guess_type

from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OAuth2Credentials

from driver import Driver

class GoogleDriveDriver(Driver):
    def __init__(self):
        super(GoogleDriveDriver, self).__init__()
        self.client_id = self.parser.get("google_drive", "client_id")
        self.client_secret = self.parser.get("google_drive", "client_secret")

    def connect(self, include_guest=False):
        try:
            credentials_json = self.parser.get("google_drive", "credentials_json")
            credentials = OAuth2Credentials.from_json(credentials_json)
            http = httplib2.Http()
            http = credentials.authorize(http)
            self.drive_service = build('drive', 'v2', http=http)
            if include_guest:
                guest_credentials_json = self.parser.get("google_drive", "guest_credentials_json")
                guest_credentials = OAuth2Credentials.from_json(guest_credentials_json)
                guest_http = httplib2.Http()
                guest_http = credentials.authorize(guest_http)
                self.guest_drive_service = build('drive', 'v2', http=guest_http)
        except Exception as e:
            print type(e), e

    def acquire_access_token(self, guest=False):
        oauth_scope = 'https://www.googleapis.com/auth/drive'
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        flow = OAuth2WebServerFlow(self.client_id, self.client_secret, oauth_scope, redirect_uri)
        authorize_url = flow.step1_get_authorize_url()
        print '1. Go to: ' + authorize_url
        print '2. Click "Allow" (you might have to log in first)'
        print '3. Copy the authorization code.'
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        if not guest:
            self.parser.set('google_drive', 'credentials_json', credentials.to_json())
        else:
            self.parser.set('google_drive', 'guest_credentials_json', credentials.to_json())
            with open(self.config_path, "w") as f:
                self.parser.write(f)

    def download(self, local_filename, remote_filename=None, remote_file_id=None):
        """Download a file's content.

        Args:
            remote_filename: the simple filename under remote root directory, optional
            remote_file_id: the id of the remote file
            local_filename: the path of the local file to be saved

        Returns:
            File's content if successful, None otherwise.
        """
        if remote_filename:
            self.download_by_filename(remote_filename=remote_filename, local_filename=local_filename)
        elif remote_file_id:
            drive_file = self._get_file_instance(remote_file_id)
            self.download_file_object(drive_file, local_filename)
        else:
            raise TypeError("download() needs at least one of the params: remote_filename or remote_file_id")

    def download_by_filename(self, remote_filename, local_filename):
        search_query = "title = '{}'".format(remote_filename)
        files = self.drive_service.files().list(q=search_query).execute()
        if len(files['items']) > 0:
            self.download_file_object(files['items'][0], local_filename)

    def download_file_object(self, drive_file, local_filename):
        """Download the file described by the Google Grive file_object

        Args:
            drive_file: the remote file's metadata
        """
        download_url = drive_file.get('downloadUrl')
        if download_url:
            resp, content = self.drive_service._http.request(download_url)
            if resp.status == 200:
                with open(local_filename, "wb") as out:
                    out.write(content)
                return content
            else:
                print 'An error occurred: %s' % resp
                return None
        else:
            # The file doesn't have any content stored on Drive.
            return None

    def retrieve_all_files(self, page_token=None):
        """Retrieve a list of File resources.

        Returns:
            List of File resources.
        """
        result = []
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                files = self.drive_service.files().list(**param).execute()

                result.extend(files['items'])
                page_token = files.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break
        return result

    def upload(self, local_filename, remote_filename):
        """Insert new file.

        Args:
            local_filename: the path to the local file to be uploaded
            remote_filename: the title of the file to be saved.
                             so far, path is not supported and it only uploads to root dir
        Returns:
            Inserted file metadata
        """
        mime_type = GoogleDriveDriver._file_mimetype(local_filename)
        media_body = MediaFileUpload(local_filename, mimetype=mime_type, resumable=False)
        body = {
            'title': remote_filename,
            'description': '',
            'mimeType': mime_type,
        }
        file = self.drive_service.files().insert(body=body, media_body=media_body).execute()
        print file
        return file

    def share(self, host_filename, guest_filename):
        pass

    @staticmethod
    def _file_mimetype(filename):
        mime_type = guess_type(filename)[0]
        mime_type = mime_type if mime_type else 'text/plain'
        return mime_type

    def _get_file_instance(self, file_id):
        try:
            file = self.drive_service.files().get(fileId=file_id).execute()
            return file
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return None


if __name__ == "__main__":
    import pprint
    gdrive = GoogleDriveDriver()
    #gdrive.acquire_access_token(guest=True)
    gdrive.connect(include_guest=True)
    #gdrive.upload("./test.txt", "lalala2.txt")
    #gdrive.download(remote_file_id="0B-hO3za-N_vrQ0FlOGE2b3ktQlk", local_filename="./test.pdf")
    #print gdrive.download_by_filename(remote_filename="lalala.txt", local_filename="la-la-la.txt")
    #gdrive.download(remote_filename="lalala.txt", local_filename="./download.txt")
    pprint.pprint(gdrive.retrieve_all_files())
