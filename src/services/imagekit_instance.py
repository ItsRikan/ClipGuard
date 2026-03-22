import os
import tempfile

import imagekitio
from imagekitio import ImageKit
from dotenv import load_dotenv

load_dotenv()
imagekit = ImageKit(
    private_key=os.environ.get("IMAGEKIT_PRIVATE_KEY"),
    
)

def list_all_files():
    final_list = []
    list_of_files = imagekit.assets.list(file_type="non-image")
    for file in list_of_files:
        data = {
            "video_id":file.file_id,
            "url":file.url
        }
        final_list.append(data)

    return final_list


