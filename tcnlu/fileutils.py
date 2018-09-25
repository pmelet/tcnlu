import os.path, json, zipfile
from os import listdir
from os.path import isfile, join

class FileAdaptor():
    def listdir(self, path):
        raise NotImplementedError("Please Implement this method")

    def json(self, *args):
        raise NotImplementedError("Please Implement this method")

    def json(self, *args):
        raise NotImplementedError("Please Implement this method")

class FolderFileAdaptor(FileAdaptor):
    def __init__(self, root):
        self.root = root

    def listdir(self, path):
        return listdir(os.path.join(self.root, path))

    def join(self, *args):
        return os.path.join(self.root, *args)

    def json(self, *args):
        filename = os.path.join(self.root, *args)
        with open(filename, encoding="utf8") as h:
            return json.load(h)

class ZipFileAdaptor():
    def __init__(self, path):
        self.archive = zipfile.ZipFile(path)

    def listdir(self, path):
        prefix = path + "/"
        return map(lambda x: x[len(prefix):], filter(lambda x: x[:len(prefix)]==prefix, self.archive.namelist()))

    def json(self, *args):
        return "/".join(args)

    def json(self, *args):
        filename = "/".join(args)
        with self.archive.open(filename) as h:
            return json.load(h)