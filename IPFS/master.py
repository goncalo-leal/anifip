import requests
import argparse
import json

def upload_file(midi_file):
    response = requests.post('http://localhost:5001/api/v0/add', files=midi_file)
    res_json = json.loads(response.text)
    print(f"File added with CID: {res_json['Hash']}")
    return res_json['Hash']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to IPFS")
    parser.add_argument("file_path", help="Path to the file to be uploaded")
    args = parser.parse_args()
    upload_file(args.file_path)