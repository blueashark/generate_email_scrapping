from bs4 import BeautifulSoup
import cloudscraper


class EmailFinder:

    def __init__(self):
        self.author = str()
        self.inst_link = str()
        self.email_id = str()
        self.website = str()

    def get_email(self, author, inst_link):
        self.author = author
        self.inst_link = inst_link

        # Prepare fname_lname
        fname = str()
        lname = str()
        split_name = self.author.split(" ")
        for n in range(len(split_name) - 1):
            fname += str(split_name[n])
        lname = str(split_name[-1])
        fname_lname = fname + "." + lname

        # Beautifulsoup to convert from name to domain
        if self.inst_link != " ":
            scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
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
                    domain = div_text_list[domain_index].split("/")[2].replace("www.", "@")
                elif div_text_list[domain_index][0] == "w":
                    domain = div_text_list[domain_index].replace("www.", "@")
            else:
                domain = "@NotFound"
                self.website = "NotFound"
        else:
            domain = "@NotFound"
            self.website = "NotFound"

        # Merge domain list and fname_lname list
        self.email_id = str(fname_lname) + str(domain)
