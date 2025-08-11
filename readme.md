
# Blanko's Agenda Data Protocol (BADP)

A hierarchical data storage system for agenda with support for categories, themes.

## Features

- **Structured Data Storage**: Organize agenda items in categories with metadata
- **Theme Support**: Attach visual themes to your agenda items
- **File-based Storage**: Single-file container format using ZIP compression
- **Hierarchical Design**: Parent-child relationships between data elements
- **Metadata Management**: Track counts, descriptions, and formats
- **Image Support**: Store theme images directly in the agenda file


## File Structure

The BADP format uses a ZIP container with the following structure:
```
file.bad/
│
├── meta.s         - Metadata
├── data.s         - Main agenda data
└── files/
    ├── theme1.png - Theme images
    └── theme2.png
```

## API Reference

### Core Classes

- **`AgendaFile`**: Main interface for agenda files
- **`AgendaMetaData`**: Manages file metadata
- **`AgendaData`**: Contains the actual agenda content
- **`CategorieMetaData`**: Metadata for categories
- **`ThemeMetaData`**: Metadata for themes
- **`Item`**: Individual agenda items

### Helper Classes

- `HierarchizedJsonLoadableData`
- `HierarchizedLoadableData`
- `ThemesData`


## Requirements

- Python 3.7+
- Pillow (for image handling)

## Documentation
[documentation](doc.md)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please open an issue or pull request for any improvements.

## Warning

The tool and the Protocol given is **not complet**, and **may contains bugs** or unpractical things that **needs to be reworked**