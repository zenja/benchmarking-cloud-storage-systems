import dropbox

from driver import Driver

class DropboxDriver(Driver):
    def __init__(self):
        super(DropboxDriver, self).__init__()
        self.app_key = self.parser.get("dropbox", "app_key")
        self.app_secret = self.parser.get("dropbox", "app_secret")

    def connect(self, include_guest=False):
        try:
            self.access_token = self.parser.get("dropbox", "access_token")
            self.client = dropbox.client.DropboxClient(self.access_token)
            #print 'linked account: ', client.account_info()
            if include_guest:
                self.guest_access_token = self.parser.get("dropbox", "guest_access_token")
                self.guest_client = dropbox.client.DropboxClient(self.guest_access_token)
        except Exception as e:
            print type(e), e

    def acquire_access_token(self, guest=False):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorize_url = flow.start()
        print '1. Go to: ' + authorize_url
        print '2. Click "Allow" (you might have to log in first)'
        print '3. Copy the authorization code.'
        code = raw_input("Enter the authorization code here: ").strip()
        # This will fail if the user enters an invalid authorization code
        access_token, user_id = flow.finish(code)
        if not guest:
            self.parser.set('dropbox', 'access_token', access_token)
            self.parser.set('dropbox', 'user_id', user_id)
        else:
            self.parser.set('dropbox', 'guest_access_token', access_token)
            self.parser.set('dropbox', 'guest_user_id', user_id)
        with open(self.config_path, "w") as f:
            self.parser.write(f)

    def upload(self, local_filename, remote_filename):
        try:
            with open(local_filename, 'rb') as f:
                response = self.client.put_file(remote_filename, f)
            return response
        except Exception as e:
            print e

    def download(self, remote_filename, local_filename):
        try:
            f, metadata = self.client.get_file_and_metadata(remote_filename)
            with open(local_filename, 'wb') as out:
                out.write(f.read())
            return f
        except Exception as e:
            print e

    def share(self, host_filename, guest_filename):
        copy_ref = self.client.create_copy_ref(host_filename)['copy_ref']
        self.guest_client.add_copy_ref(copy_ref, guest_filename)

if __name__ == "__main__":
    dbox = DropboxDriver()
    dbox.connect(include_guest=True)
    #dbox.share(host_filename="/CV_CL/Xing_CV.txt", guest_filename="/Xing_CV.txt")
    #dbox.download(remote_filename="/CV_CL/Xing_CV.pdf", local_filename="./cv.pdf")
