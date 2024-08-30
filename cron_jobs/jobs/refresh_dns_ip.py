import json
import os
import sys

import requests
from logger import get_logger

API_TOKEN = os.getenv("DESEC_TOKEN")
DOMAIN_NAME = "goosenet.cloud"
DNS_RECORD_ENDPOINT = f"https://desec.io/api/v1/domains/{DOMAIN_NAME}/rrsets/ipv4/A/"
PUBLIC_IP_ENDPOINT = "https://api.ipify.org?format=json"
logger = get_logger("refresh_dns_ip")


def get_actual_ip() -> str | None:
    """Returns the current public IP address of the router"""
    try:
        response = requests.get(PUBLIC_IP_ENDPOINT)
        response.raise_for_status()
        public_ip = response.json()["ip"]
        logger.info(f"Current public IP: {public_ip}")
        return public_ip
    except requests.RequestException as e:
        logger.error(f"Error fetching current public IP address: {e}")
        return None


def get_current_dns_ip() -> str | None:
    """Returns the current IP address associated with the domain"""
    try:
        response = requests.get(DNS_RECORD_ENDPOINT, headers={"Authorization": f"Token {API_TOKEN}"})
        response.raise_for_status()
        dns_ip = response.json()["records"][0]
        logger.info(f"Current DNS IP: {dns_ip}")
        return dns_ip
    except requests.RequestException as e:
        logger.error(f"Error fetching existing DNS record: {e}")
        return None


def update_dns_ip(public_ip: str) -> None:
    """Update the DNS record with a new IP address"""
    try:
        response = requests.patch(
            DNS_RECORD_ENDPOINT,
            headers={"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json"},
            data=json.dumps({"records": [public_ip]}),
        )
        response.raise_for_status()
        logger.info(f"Successfully updated DNS record to {public_ip}")
    except requests.RequestException as e:
        logger.error(f"Error updating DNS record: {e}")


def main():
    logger.info("Running DNS IP refresh script...")

    if not API_TOKEN:
        logger.error("Environment variable 'DESEC_TOKEN' has not been set, aborting")
        sys.exit(1)

    dns_ip = get_current_dns_ip()
    public_ip = get_actual_ip()

    if dns_ip is None or public_ip is None:
        logger.error("Failed to fetch IP addresses, aborting.")
        sys.exit(1)

    if dns_ip == public_ip:
        logger.info("DNS is up to date")
    else:
        update_dns_ip(public_ip)


if __name__ == "__main__":
    main()
