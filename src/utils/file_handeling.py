import os
import tempfile
import requests
import uuid


async def save_temp(file):
    temp = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
    content = file.read()
    temp.write(content)
    temp.close()
    return temp.name

def cleanup(path):
    if os.path.exists(path):
        os.remove(path)

def download(url):
    path = os.path.join(os.getcwd(),'temp')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path,f"{uuid.uuid4()}.mp4")
    r = requests.get(url,stream=True)

    with open(path,"wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return path

