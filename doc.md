

# BAD Protocol (Blanko's Agenda Data Protocol) Documentation

## Overview
The `badp.py` module provides classes and methods to handle agenda data files with metadata, categories, themes, and items. It uses a hierarchical structure with JSON serialization and ZIP file storage.

## Main Class

### `AgendaFile`
The main class for reading, writing, and creating agenda data files.

#### Initialization
```python
badp_file = badp.AgendaFile("example.bad")
```
- Creates a new file if `path` doesn't exist
- Loads existing file if it exists (must be valid BADP format)

#### Attributes
- **meta**: `AgendaMetaData` - Contains all metadata of the file
- **data**: `AgendaData` - Contains the actual agenda content
- **path**: `Path` - Location of the agenda file

#### Methods
- **save(path=None)**: Saves the agenda to file
  - `path`: Optional alternative save location
- **update()**: Updates internal file representation
- **close()**: Saves changes and cleans up temporary files
- **_load_from_file()**: Internal method to load existing file

---

### `AgendaMetaData`
Handles metadata for the agenda file.

#### Attributes
- **categories**: `list[CategorieMetaData]` - List of category metadata objects
- **themes**: `list[ThemeMetaData]` - List of theme metadata objects
- **data_count**: `int` - Number of data items
- **date_format**: `str` - Format string for dates (default: "MM/DD/YYYY")

#### Methods
- **from_dict(_dict, parent)**: Creates instance from dictionary
- **from_json(json, parent)**: Creates instance from JSON string

---

### `CategorieMetaData`
Metadata for agenda categories.

#### Attributes
- **name**: `str` - Category name
- **description**: `str` - Category description
- **type**: `str` - Category type
- **count**: `int` - Item count in category

---

### `ThemeMetaData`
Metadata for agenda themes.

#### Attributes
- **name**: `str` - Theme name
- **id**: `str` - Unique theme identifier

---

### `AgendaData`
Contains the actual agenda content and themes.

#### Attributes
- **themes**: `ThemesData` - Manages theme images
- **_categories**: `dict` - Internal storage of categorized items

#### Methods
- **from_dict(_dict, parent)**: Creates instance from dictionary
#### Operators
- get item : `AgendaData()["category"]`
- iter :  ```for key in AgendaData(): print(key)```

---

### `ThemesData`
Manages theme-related data and images.

#### Methods
- **add(image, name, _id=None)**: Adds a new theme
  - `image`: Path to theme image
  - `name`: Theme name
  - `_id`: Optional custom ID (auto-generated if None)
- **get_image(theme_id)**: Retrieves theme image as PIL.Image

---

### `Item`
Represents an individual agenda item.

#### Attributes
- **title**: `str` - Item title
- **content**: `str` - Item content
- **level**: `int` - Importance/priority level of the fact
- **theme**: `str` - Associated theme ID

#### Methods
- **get_image()**: Gets associated theme image
- **from_dict(_dict, parent)**: Creates instance from dictionary

---

## Helper Classes

### `HierarchizedJsonLoadableData`
Base class for JSON-loadable hierarchical data.

#### Attributes
- **KEYS**: `list` - Class-specific keys for JSON loading

#### Methods
- **from_dict(_dict, parent)**: Creates instance from dictionary
- **from_json(json, parent)**: Creates instance from JSON string

---

### `HierarchizedLoadableData`
Base class for loadable hierarchical data.

#### Methods
- **from_io(io, parent)**: Loads from file-like object
- **from_file(path, parent)**: Loads from file path
- **from_bytes(data, parent)**: Loads from bytes
- **to_bytes(parent)**: Serializes to bytes
- **unlink()**: Removes parent reference
- **link(parent)**: Sets parent reference

---

## Exceptions
- **JsonVersionError**: Raised for JSON version incompatibilities
- **InvalidFileError**: Raised for invalid file formats

---

## Usage Example

```python
# load agenda data
agenda = badp.AgendaFile("exemple.bad")

# read all the categories images
for key in badp_file.data:
    if isinstance(badp_file.data[key], dict):
        for date in badp_file.data[key]:
            print(badp_file.data[key][date].get_image())
    else:
        for item in badp_file.data[key]:
            print(item.get_image())

```

This documentation covers all major components of the BADP implementation. The hierarchical structure allows for organized storage of agenda data with associated metadata and themes.

## Warning

The tool and the Protocol given is **not complet**, and **may contains bugs** or unpractical things that **needs to be reworked**