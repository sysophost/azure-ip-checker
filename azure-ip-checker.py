import argparse
from ipaddress import ip_address, ip_network

import requests

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--ipaddress", "-i", type=str, help="IP address to check", action="append", required=True)
PARSER.add_argument("--jsonurl", "-j", type=str, default="https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20220221.json", help="Azure JSON data (default: %(default)s)", required=False)
ARGS = PARSER.parse_args()

def fetch_azure_json(url: str) -> str:
    try:
        resp = requests.get(url)
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
                    results.append({"service": v["properties"]["systemService"] if v["properties"]["systemService"] else "N/A", "region": v["properties"]["region"] if v["properties"]["region"] else "N/A", "regionId": v["properties"]["regionId"], "address_prefix": address_prefix})

        return results
    except:
        return None


if __name__ == "__main__":
    azure_json = fetch_azure_json(ARGS.jsonurl)

    for ip in ARGS.ipaddress:
        if results := check_in_range(azure_json, ip):
            for result in results:
                print(f"{ip} is in Azure region {result['region']} ({result['regionId']}) for service {result['service']} in subnet {result['address_prefix']}")
            print("*" * 100)
        else:
            print(f"{ip} is not in an in Azure region")
