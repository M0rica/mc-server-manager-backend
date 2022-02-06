import requests
from bs4 import BeautifulSoup


class AvailableMinecraftServerVersions:

    def __init__(self):
        self.available_versions = {}
        self._get_available_minecraft_versions()

    def _get_available_minecraft_versions(self):
        def get_webpage(url):
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:96.0) Gecko/20100101 Firefox/96.0"
            }
            return requests.get(url, headers=headers).text

        webpage = get_webpage("https://mcversions.net")
        soup = BeautifulSoup(webpage, "html.parser")
        releases = soup.find_all("div",
                                 {"class": "item flex items-center p-3 border-b border-gray-700 snap-start ncItem"})
        for version in releases:
            self.available_versions[version.get("id")] = "https://mcversions.net" + version.find("a", text="Download").get("href")