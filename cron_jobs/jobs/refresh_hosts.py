import sys

import docker
from eero import ClientException, Eero, SessionStorage
from logger import get_logger

HOST_PATH = "/etc/hosts"
logger = get_logger("refresh_hosts")


class CookieStore(SessionStorage):
    def __init__(self, cookie_file):
        from os import path

        self.cookie_file = path.abspath(cookie_file)

        try:
            with open(self.cookie_file, "r") as f:
                self.__cookie = f.read()
        except IOError:
            self.__cookie = None

    @property
    def cookie(self):
        return self.__cookie

    @cookie.setter
    def cookie(self, cookie):
        self.__cookie = cookie
        with open(self.cookie_file, "w+") as f:
            f.write(self.__cookie)


def get_reservations() -> dict[str:str] | None:
    """Query the router for devices and return a diotionary of ipv4:hostname for any reserved ip addresses"""
    session = CookieStore("/eero.cookie")
    eero = Eero(session)
    try:
        account = eero.account()
        network = account["networks"]["data"][0]
        devices = eero.devices(network["url"])
        hosts_dict = {d["ip"]: d["nickname"] for d in devices if d["ip"] and d["nickname"]}
    except ClientException as e:
        logger.error("Failed to retreive reservations from router: {e}")
    return hosts_dict


def read_hosts() -> dict[str:str]:
    """Returns a dictionary of ipv4:hostname from the /etc/hosts file"""
    hosts_dict = {}
    try:
        with open(HOST_PATH, "r") as f:
            lines = f.readlines()

            for line in lines:
                parts = line.strip().split()
                if parts and parts[0].count(".") == 3:
                    hosts_dict[parts[0]] = parts[1]
    except FileNotFoundError as e:
        logger.warning(f"Couldn't find hosts file at {HOST_PATH}")
    return hosts_dict


def write_hosts(hosts_dict: dict[str:str]) -> None:
    """Writes a dictionary of ipv4:hostname to the etc/hosts file"""
    ordered_hosts = {ip: hosts_dict[ip] for ip in sorted(hosts_dict, key=lambda ip: tuple(map(int, ip.split("."))))}
    with open(HOST_PATH, "w") as f:
        for ip, hostname in ordered_hosts.items():
            f.write(f"{ip.ljust(20, ' ')}  {hostname} \n")


def reload_dnsmasq() -> None:
    """Restart the dnsmasq service to allow the updated /etc/hosts to be taken in effect"""
    client = docker.from_env()
    try:
        container = client.containers.get("dnsmasq")
        container.restart()
        logger.info(f"Successfully restarted dnsmasq service")
    except Exception as e:
        logger.error(f"Failed to restart dnsmasq service: {e}")


def main():
    logger.info("Running host refresh script...")

    current_host_dict = read_hosts()
    reservations = get_reservations()

    if not reservations:
        sys.exit(1)

    if current_host_dict == reservations:
        logger.info("/etc/hosts is up to date")
    else:
        write_hosts(reservations)
        logger.info("Updated /etc/hosts, reloading dnsmasq...")
        reload_dnsmasq()


if __name__ == "__main__":
    main()
