"""This file contains details about services required
    i.e. Cloud Services  and Redis
"""
import boto3
import redis

s3 = boto3.client('s3')  # Connection for S3


def upload_image(file, tag_file, valid_image):
    """This method is used to upload the images to Amazon s3 bucket"""
    try:
        if valid_image:  # If Image is Valid
            key = tag_file  # Assign the Key
            s3.upload_fileobj(file, 'fundoobucket', Key=key)  # Upload the image in a S3
    except Exception as e:
        print(e)


def delete_from_s3(key):
    try:
        """This method is used to delete any object from s3 bucket """
        if key:  # If Key
            s3.delete_object(Bucket='fundoobucket', Key=key)  # Delete the image in a S3
    except Exception as e:
        print(e)



r = redis.StrictRedis(host='localhost', port=6379, db=0)


class redis_information:
    """This class is used to set , get and delete data from Redis cache
    In addition to the changes above, the Redis class, a subclass of StrictRedis,
    overrides several other commands to provide backwards compatibility with older
    versions of redis-py

    """

    def set_token(self, key, value):  # Set the token
        try:
            if key and value:  # If key and Value is present i.e set
                r.set(key, value)  # redis cache is set
        except Exception as e:
            print(e)

    def get_token(self, key):  # Get the token
        try:
            value = r.get(key)  # Get the key from the cache
            if value:  # if token
                return value  # return
        except Exception as e:
            print(e)
