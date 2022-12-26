import requests
import time

BIG_API = "Enter your Bigpicture API"


class EmailFinder:

    def __init__(self):
        self.author = []
        self.inst = []
        self.email_id = []

    def get_email(self, author, inst):
        self.author = author
        self.inst = inst

        # Prepare fname_lname
        fname = str()
        lname = str()
        split_name = self.author.split(" ")
        for n in range(len(split_name) - 1):
            fname += str(split_name[n])
        lname = str(split_name[-1])
        fname_lname = fname + "." + lname

        # API call to convert from name to domain
        if self.inst == " ":
            domain = "NotFound"
        else:
            bp_url_nd = "https://company.bigpicture.io/v2/companies/search"
            params_nd = {"name": self.inst}
            headers_nd = {
                    "Authorization": BIG_API
                }
            response_nd = requests.request("GET", bp_url_nd, headers=headers_nd, params=params_nd).json()
            try:
                domain = response_nd["data"][0]["domain"]
            except IndexError and KeyError:
                domain = "NotFound"
            time.sleep(0.5)

        # Merge domain list and fname_lname list
        self.email_id = str(fname_lname) + "@" + str(domain)
