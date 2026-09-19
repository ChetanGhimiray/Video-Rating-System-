import hashlib


def get_file_hash(file_path):

    hash_object = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(4096)

            if not chunk:
                break

            hash_object.update(chunk)

    return hash_object.hexdigest()
