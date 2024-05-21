import requests
import argparse

def download_file(cid, output_path):
    url = f'http://127.0.0.1:8080/ipfs/{cid}'
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"File with CID {cid} downloaded to {output_path}")
    else:
        print(f"Failed to download file with CID {cid}. HTTP Status Code: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a file from IPFS")
    parser.add_argument("cid", help="CID of the file to be downloaded")
    parser.add_argument("output_path", help="Path where the downloaded file should be saved")
    args = parser.parse_args()
    download_file(args.cid, args.output_path)