"""
A module full of useful class and functions, used in many projects by Blanko
"""

from io import BytesIO
from pathlib import Path
from pickle import loads as pickle_loads
from pickle import dumps as pickle_dumps
from zlib import compress, decompress
from os.path import getsize as path_getsize
from subprocess import run
from json import loads as json_loads

is_fernet = True

try:from cryptography.fernet import Fernet
except ImportError:is_fernet = False


def is_path(string: str):
    forbidden_chars = '/\\*?:"<>|\n\r'
    for forbidden_char in forbidden_chars:
        if forbidden_char in string:return False
    return True

def ensure_class(obj, _class):
    if not isinstance(obj, _class): return _class(obj)
    else: return obj

get_size_vbs_path = Path("get_size.vbs")
if get_size_vbs_path.exists():
    def get_size(path : str | Path):
        path = ensure_class(path, Path)
        if path.is_file(): return path_getsize(path)
        if path.is_symlink(): return 0
        if path.is_dir(): return int(run(['cscript', '/E:VBScript', 'get_size.vbs', str(path)], capture_output=True, text=True).stdout.splitlines()[-1])
        else:return 0

class InvalidUserDataBuffer(Exception):
    def __init__(self, req_class, given_class):
        super().__init__(f"Invalisd user data buffer need {req_class} got {given_class}")
        self.req_class = req_class
        self.given_class = given_class

class LoadableData:
    @classmethod
    def from_bytes(cls, data : bytes):
        data = pickle_loads(data)
        if not isinstance(data, cls): raise InvalidUserDataBuffer(cls, type(data))
        return data
    
    @classmethod
    def from_file(cls, path : str | Path):
        path = ensure_class(path, Path)
        if not path.exists():raise FileNotFoundError(path)
        return cls.from_bytes(path.read_bytes())

    @classmethod
    def from_io(cls, io: BytesIO):
        io_data = io.read()
        io.close()
        return cls.from_bytes(io_data)
    
    def to_bytes(self):
        return pickle_dumps(self)
    
    def to_file(self, io_or_path : str | Path | BytesIO):
        data = self.to_bytes()
        if isinstance(io_or_path, (str, Path)):
            path = Path(io_or_path)
            path.write_bytes(data)
        else:io_or_path.write(data)

class CommpessedLoadableData(LoadableData):
    @classmethod
    def from_bytes(cls, data):
        data = decompress()
        data = pickle_loads(data)
        if not isinstance(data, cls): raise InvalidUserDataBuffer(cls, type(data))
        return data
    
    def to_bytes(self):
        data = compress(super().to_bytes())
        return data


if is_fernet:
    class CryptedLoadableData(LoadableData):
        @classmethod
        def create_key(cls):
            return Fernet.generate_key()
        
        @classmethod
        def from_bytes(cls, data, key):
            fernet = Fernet(key)
            data = fernet.decrypt(data)
            data = pickle_loads(data)
            if not isinstance(data, cls): raise InvalidUserDataBuffer(cls, type(data))
            return data
        
        @classmethod
        def from_file(cls, path, key):
            path = ensure_class(path, Path)
            if not path.exists():raise FileNotFoundError(path)
            return cls.from_bytes(path.read_bytes(), key)

        def to_bytes(self, key):
            fernet = Fernet(key)
            data = fernet.encrypt(super().to_bytes())
            return data
        
    class CommpessedCryptedLoadableData(CommpessedLoadableData):
        @classmethod
        def create_key(cls):
            return Fernet.generate_key()
        
        @classmethod
        def from_bytes(cls, data, key):
            fernet = Fernet(key)
            data = fernet.decrypt(data)
            data = decompress(data)
            data = pickle_loads(data)
            if not isinstance(data, cls): raise InvalidUserDataBuffer(cls, type(data))
            return data
        
        @classmethod
        def from_file(cls, path, key):
            path = ensure_class(path, Path)
            if not path.exists():raise FileNotFoundError(path)
            return cls.from_bytes(path.read_bytes(), key)

        def to_bytes(self, key):
            fernet = Fernet(key)
            data = fernet.encrypt(super().to_bytes())
            return data

class JsonLoadableData:
    KEYS = []
    @classmethod
    def from_dict(cls, _dict : dict):
        obj = cls()
        for key in cls.KEYS:
            obj.__dict__[key] = _dict[key]
        return obj
    
    @classmethod
    def from_json(cls, json: str):
        _dict = json_loads(json)
        return cls.from_dict(_dict)
