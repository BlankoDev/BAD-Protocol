# Blanko's Agenda Data Protocol

from pathlib import Path
from json import loads as json_loads
from zipfile import ZipFile, is_zipfile
from utils import LoadableData, JsonLoadableData, ensure_class
from PIL import Image
from uuid import uuid1
from tempfile import gettempdir
from os import remove
from shutil import rmtree

tempdir = Path(gettempdir())

class JsonVersionError(Exception): pass
class InvalidFileError(Exception): pass

class HierarchizedJsonLoadableData:
    KEYS = []
    def __init__(self, parent):
        self._parent = parent

    @classmethod
    def from_dict(cls, _dict : dict, parent):
        obj = cls(parent)
        for key in cls.KEYS:
            obj.__dict__[key] = _dict[key]
        return obj
    
    @classmethod
    def from_json(cls, json: str, parent):
        _dict = json_loads(json)
        return cls.from_dict(_dict, parent)
    


class HierarchizedLoadableData(LoadableData):
    def __init__(self, parent):
        self._parent = parent

    @classmethod
    def from_io(cls, io, parent):
        obj = LoadableData.from_io(io)
        obj._parent = parent
        return obj
    
    @classmethod
    def from_file(cls, path, parent):
        obj = LoadableData.from_file(path)
        obj._parent = parent
        return obj

    @classmethod
    def from_bytes(cls, data, parent):
        obj = LoadableData.from_bytes(data)
        obj._parent = parent
        return obj
    
    def to_bytes(self, parent):
        self.unlink()
        data = super().to_bytes()
        self.link(parent)
        return data
    
    def unlink(self):
        """
        unlink class from parent (for saving only, this makes the class unusabe untill the link method is used)
        """
        self._parent = None
    
    def link(self, parent):
        self._parent = parent

class CategorieMetaData(JsonLoadableData):
    KEYS = ["name", "description", "type", "count"]
    def __init__(self, name: str = None, description: str = None, _type: str = None, count: int = 0):
        self.name = name
        self.description = description
        self.count = count
        self.type = _type

class ThemeMetaData(JsonLoadableData):
    KEYS = ["name", "id"]
    def __init__(self, name: str = None, _id: str = None):
        self.name = name
        self.id = _id
  
class AgendaMetaData(HierarchizedLoadableData):
    KEYS = [["categories", CategorieMetaData], ["themes", ThemeMetaData]]
    def __init__(self, parent = None):
        self._parent : AgendaFile
        super().__init__(parent)

        self.categories : list[CategorieMetaData] = []
        self.themes : list[ThemeMetaData] = []
        self.data_count = 0
        self.date_format = "MM/DD/YYYY"
    
    @classmethod
    def from_dict(cls, _dict: dict, parent):
        obj = cls(parent)
        obj.date_format = _dict["date_format"]
        obj.data_count = _dict["data_count"]
        for key in cls.KEYS: 
            for data in _dict[key[0]]:
                obj.__dict__[key[0]].append(key[1].from_dict(data))
        obj._parent.update()
        return obj

            
class ThemesData:
    def __init__(self, parent):
        self._parent : AgendaData = parent
    
    def add(self, image: str | Path, name: str, _id: str | None = None):
        _id = uuid1().hex if _id is None else _id
        image = ensure_class(image, Path)
        file_path = self._parent._parent._temp_files_dir / f"{_id}.png"
        file_path.write_bytes(image.read_bytes())

        meta = ThemeMetaData(name, _id)
        if meta not in self._parent._parent.meta.themes: self._parent._parent.meta.themes.append(meta)
        self._parent._parent.update()
    
    def get_image(self, theme_id: str):
        data = self._parent._parent._temp_files_dir / f"{theme_id}.png"
        data = data.open()
        return Image.open(data)

class AgendaData(HierarchizedLoadableData):
    def __init__(self, parent = None):
        self._parent : AgendaFile
        super().__init__(parent)
        self._categories = {}
        self.themes = ThemesData(self)
    

    @classmethod
    def from_dict(cls, _dict: dict, parent):
        obj = cls(parent)
        for key in _dict:
            current = _dict[key]
            if isinstance(current, dict):
                obj._categories[key] = {}
                for date in current: obj._categories[key][date] = Item.from_dict(current[date], obj)
            elif isinstance(current, list):
                obj._categories[key] = []
                for item in current: obj._categories[key].append(Item.from_dict(item, obj))
        obj._parent.update()
        return obj

    def __getitem__(self, key: str) -> dict | list:
        return self._categories[key]

    def __iter__(self):
        return self._categories.__iter__()


class Item:
    def __init__(self, title: str, content: str, level: int, theme: str, parent):
        self.title = title
        self.content = content
        self.level = level
        self.theme = theme
        self._parent : AgendaData = parent
    
    def get_image(self):
        data = self._parent._parent._temp_files_dir / f"{self.theme}.png"
        data = data.open("rb")
        return Image.open(data)
    
    @classmethod
    def from_dict(cls, _dict: dict, parent): # for some reason of early dev choices this class can not use JsonLoadableData
        content = _dict["content"] if "content" in _dict else ""
        for data_key in _dict:
            if data_key in ["title", "level", "content", "theme"]: continue
            content = content + "\n\r" + _dict[data_key]
        
        if content.startswith("\n\r"): content.removeprefix("\n\r")

        obj = cls(
            parent=parent,
            title=_dict["title"],
            content=content,
            level=_dict["level"],
            theme=_dict["theme"]
        )
        return obj

class AgendaFile:
    def __init__(self, path : str | Path):
        self._temp_path = tempdir / uuid1().hex
        self._temp_path.mkdir()

        self._temp_files_dir = self._temp_path / "files"
        self._temp_files_dir.mkdir()

        self.path = Path(path) if not isinstance(path, Path) else path

        if self.path.exists():
            self._load_from_file()
            return
        
        self.meta = AgendaMetaData(self)
        self.data = AgendaData(self)


    def save(self, path: str | Path | None = None):
        """
        Save the object into the file

        `path` : the path where the file will be saved (this is mostly used to save a copy elsewhere)
        """
        if path is None: path = self.path
        if path.exists(): remove(path)

        zip_file_w = ZipFile(path, "w")
        for item in self._temp_path.iterdir():
            zip_file_w.write(item, item.name)
            if item.is_dir():
                for file in item.iterdir(): zip_file_w.write(file, file.parent.name + "/" + file.name)
        zip_file_w.close()

    def update(self):
        meta = self.meta.to_bytes(self)
        data = self.data.to_bytes(self)

        meta_path = self._temp_path / "meta.s"
        data_path = self._temp_path / "data.s"

        meta_path.write_bytes(meta)
        data_path.write_bytes(data)

        self.save()

    def close(self):
        self.update()
        rmtree(self._temp_path)
        del(self)

    def _load_from_file(self):
        if not is_zipfile(self.path): raise InvalidFileError(f"the file '{self.path}' is not a '.bad' file\n\tnot a zip file Error")
        file_r = ZipFile(self.path)

        files_names = file_r.namelist()
        if "data.s" not in files_names: raise InvalidFileError(f"the file '{self.path}' is not a '.bad' file \n\tno data section Error")
        if "meta.s" not in files_names: raise InvalidFileError(f"the file '{self.path}' is not a '.bad' file \n\tno meta section Error")
        
        meta_file = file_r.open("meta.s")
        data_file = file_r.open("data.s")

        self.meta : AgendaMetaData = AgendaMetaData.from_io(meta_file, self)
        self.data : AgendaData = AgendaData.from_io(data_file, self)

        
        file_r.extractall(self._temp_path)

        file_r.close()
    
    @classmethod
    def from_dicts(cls, meta: dict, data: dict, path: str | Path):
        obj = cls(path)
        obj.meta = AgendaMetaData.from_dict(meta, obj)
        obj.data = AgendaData.from_dict(data, obj)
        return obj

