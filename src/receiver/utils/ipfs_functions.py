import requests
import argparse
import json


def upload_file(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post('http://localhost:5001/api/v0/add', files=files)
    res_json = json.loads(response.text)
    print(f"File added with CID: {res_json['Hash']}")
    return res_json['Hash']

def download_file(cid, output_path):
    url = f'http://10.1.1.15:8080/ipfs/{cid}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)
        
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"File with CID {cid} downloaded to {output_path}")
        return True
    except requests.RequestException as e:
        print(f"Failed to download file with CID {cid}: {e}")
        return False
