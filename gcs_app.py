import os
import google.cloud.storage as storage
import time
import datetime


class GCS:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloudServiceaccount.json"
        self.storage_client = storage.Client.from_service_account_json(
            'cloudServiceaccount.json')
        self.storage_client = storage.Client()
        self.bucket_name = "encrypted_data_bucket"
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def upload_cs_file(self, username, source_file, destination_file_name):
        # Destination file name is the name of the file in the bucket
        # Destination = username + filename etc. usernmaeA/file1.txt
        destination_file_name = username + "/" + destination_file_name
        blob = self.bucket.blob(destination_file_name)
        source_file.stream.seek(0)
        blob.upload_from_file(source_file.stream)

        # get_metadata = self.get_metadata(destination_file_name)

        return True

    def get_metadata(self, username, source_file_name):
        source_file_name = username+"/"+source_file_name

        blob = self.bucket.get_blob(source_file_name)

        name = blob.name
        size = blob.size
        type = blob.content_type
        gen = blob.generation
        gen = (int(gen/1000000))
        gen = datetime.datetime.fromtimestamp(gen)
        metadata = {
            'name': name,
            'size': size,
            'type': type,
            'gen': gen
        }

        return metadata

    def download_cs_file(self, source_file_name):
        bucket_name = 'encrypted_data_bucket'
        folder_name = '4514fc2e15b978b11fd46b9ca997ee7ec4fc48e517c1413122a587621f9fb3cc'
        file_name = 'key.bin'

        blob = self.bucket.blob(folder_name + '/' + file_name)
        file = blob.download_as_bytes()
        file_type = blob.content_type

        return file, file_type

    def get_public_url(self, source_file_name):

        blob = self.bucket.blob(source_file_name)
        expier_time = int(time.time() + 3600)
        url = blob.generate_signed_url(expier_time)

        return url

    # Create GCS folder
    def create_folder(self, destination_folder_name):
        if (not (destination_folder_name.endswith('/'))):
            destination_folder_name = destination_folder_name + \
                "/"  # '''Remove last character from string'''
        blob = self.bucket.blob(destination_folder_name)

        blob.upload_from_string('')
        print('Created {} .'.format(
            destination_folder_name))

    def list_blobs(self, username):
        folder_name = username
        blobs = self.bucket.list_blobs(prefix=folder_name)

    # Convert the blobs to a list of dictionaries
        files = []
        for blob in blobs:
            file = {
                'name': blob.name.replace(folder_name, '', 1),
                'download_url': blob.generate_signed_url(expiration=int(time.time()+300), method='GET'),
            }
            files.append(file)
        return files

    def get_server_private_key(self):
        blob = self.bucket.blob('private_key.pem')
        # Read the content of the file
        file_content = blob.download_as_bytes()
        # Return the content of the file as a string
        return file_content.decode('utf-8')

    def get_cs_file(self,filename):
        
        blob = self.bucket.blob(filename)
        file_contents = blob.download_as_bytes()
        return file_contents



    def delete_file(self, username, source_file_name):
        source_file_name = username+"/"+source_file_name
        blob = self.bucket.blob(source_file_name)
        blob.delete()
        return True

    