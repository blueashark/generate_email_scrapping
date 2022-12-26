from bs4 import BeautifulSoup
import cloudscraper
from email_formatter import EmailFormatter
import time


class EmailFinder:

    def __init__(self):
        self.author = str()
        self.inst_link = str()
        self.email_id = str()
        self.website = str()

    def get_email(self, author, inst_link):
        self.author = author
        self.inst_link = inst_link

        # Prepare email components like first name, last name etc
        first_name = str()
        last_name = str()
        domain = str()
        split_name = author.split(" ")
        for n in range(len(split_name) - 1):
            first_name += str(split_name[n])
        last_name = str(split_name[-1])
        try:
            first_initial = first_name[0]
        except IndexError:
            first_initial = ""
        try:
            last_initial = last_name[0]
        except IndexError:
            last_initial = ""

        # Beautifulsoup to convert from name to domain
        domain = "NotFound"
        self.website = "NotFound"
        if self.inst_link != " ":
            scraper = cloudscraper.create_scraper(delay=10, browser='chrome', captcha={'provider': 'return_response'})
            url = self.inst_link
            info = scraper.get(url).text
            soup = BeautifulSoup(info, "html.parser")

            div_text_list = []
            for div in soup.findAll('div', attrs={'class': 'nova-legacy-e-text nova-legacy-e-text--size-m nova-legacy-e-text--family-sans-serif nova-legacy-e-text--spacing-none nova-legacy-e-text--color-inherit'}):
                div_text_list.append(div.text)
            if "Website" in div_text_list:
                domain_index = div_text_list.index("Website") + 1
                self.website = div_text_list[domain_index]
                if div_text_list[domain_index][0] == "h":
                    domain = div_text_list[domain_index].split("/")[2].replace("www.", "")
                elif div_text_list[domain_index][0] == "w":
                    domain = div_text_list[domain_index].replace("www.", "")

        # Merge domain list and email format
        if domain == "NotFound":
            self.email_id = "NotFound"
        else:
            email_formatter = EmailFormatter()
            time.sleep(1)
            email_formatter.find_email_format(domain)
            email_format = email_formatter.email_format
            if email_format == "first_name last_initial":
                self.email_id = first_name + last_initial + "@" + str(domain)
            if email_format == "last_name first_initial":
                self.email_id = last_name + first_initial + "@" + str(domain)
            if email_format == "first_name":
                self.email_id = first_name + "@" + str(domain)
            if email_format == "last_name":
                self.email_id = last_name + "@" + str(domain)
            if email_format == "first_initial last_name":
                self.email_id = first_initial + last_name + "@" + str(domain)
            if email_format == "first_name.last_name":
                self.email_id = first_name + "." + last_name + "@" + str(domain)
            if email_format == "first_name_last_name":
                self.email_id = first_name + "_" + last_name + "@" + str(domain)
            else:
                self.email_id = first_name + "." + last_name + "@" + str(domain)
