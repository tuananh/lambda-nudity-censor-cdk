"""lambda censoring function"""

import re
import os
import boto3
from nudenet import NudeDetector
from matplotlib import pyplot as plt
from matplotlib import patches as patches
from PIL import Image

nude_detector = NudeDetector()
s3_client = boto3.client("s3")

SUPPORTED_EXT_REGEX = r"raw/.+\.(jpg|jpeg|png)"
BUCKET = os.environ["BUCKET"]

TEMP_INPUT_DIR = "/tmp/input_images"
TEMP_OUTPUT_DIR = "/tmp/output_images"

if not os.path.exists(TEMP_INPUT_DIR):
    os.mkdir(TEMP_INPUT_DIR)
if not os.path.exists(TEMP_OUTPUT_DIR):
    os.mkdir(TEMP_OUTPUT_DIR)

def handler(event, _context):
    print("start censoring...")
    object_key: str = event["detail"]["object"]["key"]
    if not re.match(SUPPORTED_EXT_REGEX, object_key, re.IGNORECASE):
        print(f"unsupported input object: {object_key}")
        return

    _, image_name = os.path.split(object_key)
    temp_image_path = f"{TEMP_INPUT_DIR}/{image_name}"
    s3_client.download_file(BUCKET, object_key, temp_image_path)
    
    detection_result = nude_detector.detect(temp_image_path)

    # process the image and save to tmp before uploading to s3
    im = Image.open(temp_image_path)
    fig, ax = plt.subplots()
    ax.imshow(im)

    IGNORE_CLASS_LIST = ['BELLY_EXPOSED', 'FACE_FEMALE']
    for item in detection_result:
        print(item)
        if item['class'] not in IGNORE_CLASS_LIST:
            rect = patches.Rectangle((item['box'][0], item['box'][1]), item['box'][2], item['box'][3], linewidth=1, edgecolor='black', facecolor='black')
            ax.add_patch(rect)

    temp_output_path = f"/{TEMP_OUTPUT_DIR}/{image_name}"
    plt.savefig(temp_output_path)
    s3_client.upload_file(temp_output_path, BUCKET, f"processed/{image_name}")

if __name__ == "__main__":
    handler({}, None)
