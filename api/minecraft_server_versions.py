import requests
from bs4 import BeautifulSoup


class AvailableMinecraftServerVersions:

    def __init__(self):
        self.available_versions = {}
        self._get_available_minecraft_versions()  # load on init
        print(self.available_versions)

    def _get_webpage(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:96.0) Gecko/20100101 Firefox/96.0"
        }
        return requests.get(url, headers=headers).text

    def _get_available_minecraft_versions(self):

        webpage = self._get_webpage("https://mcversions.net")
        soup = BeautifulSoup(webpage, "html.parser")
        releases = soup.find_all("div",
                                 {"class": "item flex items-center p-3 border-b border-gray-700 snap-start ncItem"})
        for version in releases:
            version_link = version.find("a", text="Download").get("href")
            if not version_link.startswith("/download/b") and not version_link.startswith("/download/a") \
                    and not version_link.startswith("/download/1.1") and not version_link.startswith("/download/1.0") \
                    and not version_link.startswith("/download/c") and not version_link.startswith("/download/rd") \
                    and not version_link.startswith("/download/inf"):
                self.available_versions[version.get("id")] = "https://mcversions.net" \
                                                             + version.find("a", text="Download").get("href")

    def get_download_link(self, version:str):
        url = self.available_versions[version]
        webpage = self._get_webpage(url)
        soup = BeautifulSoup(webpage, "html.parser")
        download_button = soup.find("a", text="Download Server Jar")
        download_link = download_button.get("href")
        print(download_button.get("download"))
        return download_link
