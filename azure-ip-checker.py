import argparse
from ipaddress import ip_address, ip_network

import requests
from bs4 import BeautifulSoup

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--ipaddress", "-i", type=str, help="IP address to check", action="append", required=True)
PARSER.add_argument("--downloadurl", "-d", type=str, default="https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519", help="Azure JSON data (default: %(default)s)", required=False)
ARGS = PARSER.parse_args()

def fetch_azure_json(url: str) -> str:
    try:
        resp = requests.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")
        json_link = soup.find("a", {"data-bi-containername":"download retry"})["href"] 

        resp = requests.get(json_link)
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.HTTPError as err:
        print(f"[!] {err}")

def check_in_range(azure_json: str, target_ip: str):
    try:
        results = list()
        for v in azure_json["values"]:
            for address_prefix in v["properties"]["addressPrefixes"]:
                subnet = ip_network(address_prefix)

                if ip_address(target_ip) in subnet:
                    results.append({"service": v["properties"]["systemService"] or "N/A", "region": v["properties"]["region"] or "N/A", "regionId": v["properties"]["regionId"], "address_prefix": address_prefix})

        return results
    except:
        return None


if __name__ == "__main__":
    azure_json = fetch_azure_json(ARGS.downloadurl)

    for ip in ARGS.ipaddress:
        if results := check_in_range(azure_json, ip):
            for result in results:
                print(f"{ip} is in Azure region {result['region']} ({result['regionId']}) for service {result['service']} in subnet {result['address_prefix']}")
            print("*" * 100)
        else:
            print(f"{ip} is not in an in Azure region")
