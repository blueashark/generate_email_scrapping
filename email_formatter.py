from bs4 import BeautifulSoup
import requests


class EmailFormatter:

    def __init__(self):
        self.email_format = str()

    def find_email_format(self, domain):
        domain = domain.strip()
        url = f"https://www.email-format.com/i/search_result/?q={domain}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.114 Safari/537.36 "
        }
        response = requests.get(url, headers=headers).text
        soup = BeautifulSoup(response, "html.parser")
        domain_link = str()
        self.email_format = "first_name.last_name"
        domains_element = soup.find_all("td", class_="td_email")
        if domains_element:
            for d in domains_element:
                dom = str(d.find("a").getText().strip())
                if dom == domain:
                    domain_link = "https://www.email-format.com" + d.find("a").get("href")
                    break
            search_response = requests.get(domain_link, headers=headers).text
            soup = BeautifulSoup(search_response, "html.parser")
            confidence_element = soup.find("div", class_="pl1 span8")
            if confidence_element:
                highest_confidence_elements = confidence_element.find_all("div", class_="format_score_container")
                self.email_format = highest_confidence_elements[0].find("div", class_="format fl").getText()
                email_format_list = self.email_format.split()
                self.email_format = ''.join(email_format_list)
