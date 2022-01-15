import os

from lxml import etree


class TxtLabelExporter(object):
    def __init__(self, export_dir: str, classes: [str]):
        self.export_dir = export_dir
        self._txt_fp = None

    def begin_export(self, image, rel_image_path: str):
        rel_label_path = os.path.splitext(rel_image_path)[0]
        self._txt_fp = open(os.path.join(self.export_dir, rel_label_path + '.txt'), 'w')

    def export_bbox(self, cls: int, tl_x: int, tl_y: int, width: int, height: int, conf: float):
        line = (cls, tl_x, tl_y, width, height, conf) if conf is not None else (cls, tl_x, tl_y, width, height)
        self._txt_fp.write(('%g ' * len(line)).rstrip() % line + '\n')

    def end_export(self):
        if self._txt_fp is not None:
            self._txt_fp.close()
        self._txt_fp = None


class VocLabelExporter(object):
    def __init__(self, export_dir: str, classes: [str], ext: str):
        self.export_dir = export_dir
        self.classes = classes
        self.ext = ext
        self.root = None
        self.image_height = self.image_width = None

    def _create_sub_element(self, parent_elt, child_elt_name, child_elt_value):
        child = etree.SubElement(parent_elt, child_elt_name)
        child.text = str(child_elt_value)
        return child

    def begin_export(self, image, rel_image_path: str):
        self.image_height, self.image_width = image.shape[:2]
        self.rel_image_path = rel_image_path

        self.root = etree.Element('annotation')
        self._create_sub_element(self.root, 'folder', '')
        self._create_sub_element(self.root, 'filename', os.path.basename(rel_image_path))
        self._create_sub_element(self.root, 'path', rel_image_path)

        elt = etree.SubElement(self.root, 'source')
        self._create_sub_element(elt, 'database', '')

        elt = etree.SubElement(self.root, 'size')
        self._create_sub_element(elt, 'width', self.image_width)
        self._create_sub_element(elt, 'height', self.image_height)
        self._create_sub_element(elt, 'depth', image.shape[2] if len(image.shape) > 2 else 1)

        self._create_sub_element(self.root, 'segmented', 0)

    def export_bbox(self, cls: int, tl_x: int, tl_y: int, width: int, height: int, conf: float):
        object_elt = etree.SubElement(self.root, 'object')
        self._create_sub_element(object_elt, 'name', self.classes[cls])
        self._create_sub_element(object_elt, 'pose', 'Unspecified')
        self._create_sub_element(object_elt, 'truncated', 0)
        self._create_sub_element(object_elt, 'difficult', 0)
        if conf is not None:
            self._create_sub_element(object_elt, 'score', conf)

        # Re-scale values to image dimensions
        tl_x = int(tl_x * self.image_width)
        tl_y = int(tl_y * self.image_height)
        width = int(width * self.image_width)
        height = int(height * self.image_height)

        bb_elt = etree.SubElement(object_elt, 'bndbox')
        self._create_sub_element(bb_elt, 'xmin', tl_x)
        self._create_sub_element(bb_elt, 'ymin', tl_y)
        self._create_sub_element(bb_elt, 'xmax', tl_x + width)
        self._create_sub_element(bb_elt, 'ymax', tl_y + height)

        self.root.extend([object_elt])

    def end_export(self):
        rel_label_path = os.path.splitext(self.rel_image_path)[0]
        etree.ElementTree(self.root).write(os.path.join(self.export_dir, rel_label_path + self.ext), pretty_print=True)
        self.root = None
        self.image_height = self.image_width = None
