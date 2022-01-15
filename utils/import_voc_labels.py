"""
Code suitable for use within a ./data/*.yml file's `download:` section.
Converts all Pascal VOC labels in a given dir to the label format needed by this YOLOv5 training code.
"""
import glob
import os
from pathlib import Path

import cv2
from tqdm import tqdm
import xml.etree.ElementTree as ET
import yaml as yaml_package

MIN_IMAGE_DIM = 1024


def convert_label(path, lb_path, yaml):
    def convert_box(size, box):
        dw, dh = 1. / size[0], 1. / size[1]
        x, y, w, h = (box[0] + box[1]) / 2.0 - 1, (box[2] + box[3]) / 2.0 - 1, box[1] - box[0], box[3] - box[2]
        return x * dw, y * dh, w * dw, h * dh

    in_file = open(path)
    out_file = open(lb_path, 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls in yaml['names'] and not int(obj.find('difficult').text) == 1:
            xmlbox = obj.find('bndbox')
            bb = convert_box((w, h), [float(xmlbox.find(x).text) for x in ('xmin', 'xmax', 'ymin', 'ymax')])
            cls_id = yaml['names'].index(cls)  # class id
            out_file.write(" ".join([str(a) for a in (cls_id, *bb)]) + '\n')


def _resize(img):
    if img.shape[0] > MIN_IMAGE_DIM * 2 or img.shape[1] > MIN_IMAGE_DIM * 2:
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    return img


def do_yolov5_prep(yaml: dict):
    dataset_root = Path(yaml['path'])

    # Convert by putting images in:
    #   /tmp/yolov5/images/trailcam_picts_original/
    # Labels in:
    #   /tmp/yolov5/labels/trailcam_picts_original/
    for tvt_set in ['train', 'val', 'test']:
        for dataset_path in yaml[tvt_set]:
            for cls in yaml['names']:
                dataset_path = dataset_path.rstrip(os.sep)
                dataset_name = os.path.split(dataset_path)[-1]
                imgs_dir = dataset_root / dataset_name / 'originals' / cls
                g = glob.iglob(str(imgs_dir / '*.[jJ][pP][gG]'), recursive=True)
                for image_path in tqdm(list(g)):
                    image_path = Path(image_path)
                    filename = os.path.split(image_path)[1]
                    base_filename, image_ext = os.path.splitext(filename)
                    xml_label_filename = base_filename + '.xml'
                    xml_label_path = imgs_dir / xml_label_filename
                    if xml_label_path.is_file():
                        dest_img_path = dataset_root / dataset_path
                        dest_img_path.mkdir(exist_ok=True, parents=True)

                        yolov5_label_dir = dest_img_path / '..' / '..' / 'labels' / dataset_name
                        yolov5_label_dir.mkdir(exist_ok=True, parents=True)
                        yolov5_label_file = yolov5_label_dir / (cls + '_' + base_filename + '.txt')

                        try:
                            img = cv2.imread(str(image_path))
                        except Exception as ex:
                            print(f'Could not read {image_path}: {str(ex)}')
                            continue
                        if img is None:
                            continue
                        img = _resize(img)
                        dest_img_path = dest_img_path / (cls + '_' + image_path.name)
                        cv2.imwrite(str(dest_img_path), img)
                        # The conversion from VOC to YOLO format only requires that the information in the VOC file
                        # about the image dimensions and the various bbox coordinates be correct. The fact that we
                        # resize (reduce) the size of the image above doesn't matter since VOC bbox values are all
                        # normalized to 0 <= coordinate <= 1.0 and are thus invariant to the size of the image in
                        # the image file itself.
                        convert_label(xml_label_path, yolov5_label_file, yaml)  # convert labels to YOLO format


if __name__ == "__main__":
    yaml = yaml_package.load(open('/Users/jimmeyer/git-oss/yolov5/data/trailcam_10_class_jan_2022.yaml'), Loader=yaml_package.SafeLoader)
    do_yolov5_prep(yaml)
