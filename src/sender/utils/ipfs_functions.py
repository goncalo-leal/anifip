import requests
import argparse
import json


def upload_file(file_path):
    print(file_path)
    files = {'file': open(file_path, 'rb')}
    response = requests.post('http://localhost:5001/api/v0/add', files=files)
    res_json = json.loads(response.text)
    print(f"File added with CID: {res_json['Hash']}")
    return res_json['Hash']

def download_file(cid, output_path):
    url = f'http://127.0.0.1:8080/ipfs/{cid}'
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"File with CID {cid} downloaded to {output_path}")
    else:
        print(f"Failed to download file with CID {cid}. HTTP Status Code: {response.status_code}")