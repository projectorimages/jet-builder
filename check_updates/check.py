import json
import os
from urllib.request import urlopen

from docker_registry_client import DockerRegistryClient
from semantic_version import Version

ide_repos = {
    "IIU": "projector-idea-u",
    "IIC": "projector-idea-c",
    "PCP": "projector-pycharm-p",
    "PCC": "projector-pycharm-c",
    "RM": "projector-rubymine",
    "RD": "projector-rider",
    "CL": "projector-clion",
    "GO": "projector-goland",
    "WS": "projector-webstorm",
    "DG": "projector-datagrip"
}

organization = "projectorimages"

if __name__=="__main__":
    registry_username = os.getenv("REGISTRY_USERNAME")
    registry_password = os.getenv("REGISTRY_PASSWORD")

    product_codes = ",".join(ide_repos.keys())
    url = "https://data.services.jetbrains.com/products?code=" + product_codes + "&release.type=release"
    data: list = json.loads(urlopen(url).read())

    dh = DockerRegistryClient('https://hub.docker.com', username=registry_username, password=registry_password)

    latest_releases = list()
    for code, repository in ide_repos.items():
        tags = dh.repository(repository, organization).tags()
        tags.remove("latest")
        tags = [Version.coerce(tag) for tag in tags]
        latest_tag = max(tags)
        latest_version = Version.coerce(next(product["releases"][0]["version"] for product in data if product["code"] == code))

        if latest_version > latest_tag:
            release = dict()
            release["image"] = organization + "/" + repository
            release["version"] = next(product["releases"][0]["version"] for product in data if product["code"] == code)
            release["download"] = next(product["releases"][0]["downloads"]["linux"]["link"] for product in data if product["code"] == code)
            latest_releases.append(release)

    print(latest_releases)