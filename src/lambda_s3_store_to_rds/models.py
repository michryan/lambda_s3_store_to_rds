from dataclasses import dataclass

@dataclass
class ImageProperties:
    name: str
    size: str
    mime: str
    width: str
    height: str

@dataclass
class TableEntry:
    image_id: str
    file_name: str
    file_size: str
    file_type: str  
    image_width: str
    image_height: str
    timestamp: str