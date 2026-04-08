import json
import xml.etree.ElementTree as ET
import os

def update_material_colors(xml_path, color_config: dict) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    for bsdf in root.iter("bsdf"):
        mat_id = bsdf.get("id")
        if mat_id in color_config:
            rgb_tag = bsdf.find("rgb")
            if rgb_tag is None:
                rgb_tag = ET.SubElement(bsdf, "rgb", name="reflectance")
            rgb_tag.set("value", color_config[mat_id])
            
    tree.write(xml_path, xml_declaration=True, encoding="utf-8")

def set_shape_ids_from_filename(xml_path, output_path=None, extension=".ply"):
    if output_path is None:
        output_path = xml_path
        
    stats = {'updated': 0, 'skipped': 0, 'errors': []}
    
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for shape in root.findall(".//shape"):
        filename_elem = shape.find("./string[@name='filename']")
        if filename_elem is None:
            stats['skipped'] += 1
            continue
            
        value = filename_elem.get("value")
        if not value or not value.lower().endswith(extension):
            stats['skipped'] += 1
            continue
            
        try:
            basename = os.path.basename(value)
            name_without_ext = os.path.splitext(basename)[0]
            shape.set("id", name_without_ext)
            shape.set("name", name_without_ext)
            stats['updated'] += 1
        except Exception as e:
            stats['errors'].append(f"Error processing {value}: {str(e)}")

    tree.write(output_path, xml_declaration=True, encoding="utf-8")
    return stats

def apply_materials_from_config(scene, config: dict) -> None:
    for name, props in config.items():
        obj = scene.get(name)
        if obj is not None:
            obj.radio_material = props["radio_material"]
            obj.thickness = props["thickness"]
        else:
            print(f"Warning: Object '{name}' not found in scene.")