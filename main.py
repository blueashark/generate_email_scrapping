import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ast
import openpyxl
from email_finder import EmailFinder
from bs4 import BeautifulSoup
import cloudscraper
import datetime

topic_dict = {
    "genomics": "https://www.researchgate.net/topic/Genomics/publications",
    "gene_expression": "https://www.researchgate.net/topic/Gene-Expression/publications",
    "gene_regulation": "https://www.researchgate.net/topic/Gene-Regulation/publications",
    "epigenetics": "https://www.researchgate.net/topic/Epigenetics/publications",
    "genetics": "https://www.researchgate.net/topic/Genetics/publications",
    "covid_19": "https://www.researchgate.net/topic/COVID-19/publications"
}
print("Please read the instructions file carefully!")
topic = input("Select a topic (covid_19/genetics/epigenetics/gene_regulation/gene_expression/genomics): ")
chromedriver_location = input("Enter the location of chromedriver on your pc (e.g./Users/satyaprakashsahoo/Documents/Chrome Driver/chromedriver): ")
nos = int(input("How many articles you want to search?: "))

# Create dataframe and empty csv to store all scrapped information
df = pd.DataFrame({'Title': [],
                   'Author_Institution': []
                   })
df.to_csv(f'{topic}.csv', index=False)

start_time = datetime.datetime.now()  # To calculate the time for scraping
# Initiate selenium driver
ser = Service(chromedriver_location)
driver = webdriver.Chrome(service=ser)
driver.get(topic_dict[f"{topic}"])

# Search for number of articles mentioned by scrolling through pages and build a list of all article links
next_page_element = True
article_link_list = []
n = 0
while next_page_element and n < nos:
    article_link_elements = driver.find_elements(By.XPATH,
                                                 '//*[@id="lite-page"]/main/section[3]/div[4]/div/div/div/div/div/div/div[2]/div/a')
    for article in article_link_elements:
        article_link = article.get_attribute("href")
        article_link_list.append(article_link)

    try:
        next_page_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                            '//*[@id="lite-page"]/main/section[3]/div[4]/div/div/div[100]/div/div/div/div[1]/div/div[12]/a')))
        next_page_element.click()
    except ElementClickInterceptedException:
        footer_element = driver.find_element(By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[3]')
        footer_element.click()
        next_page_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                            '//*[@id="lite-page"]/main/section[3]/div[4]/div/div/div[100]/div/div/div/div[1]/div/div[12]/a')))
        next_page_element.click()

    n += len(article_link_list)
driver.quit()
# Browse through each article link and get the required details. Store them in csv format.
i = 0
for link in article_link_list[:nos]:
    scraper = cloudscraper.create_scraper(delay=10, browser='chrome', captcha={'provider': 'return_response'})
    info = scraper.get(link).text
    soup = BeautifulSoup(info, "html.parser")
    # Find article name
    try:
        article_name_element = soup.find("h1",
                                         class_="nova-legacy-e-text nova-legacy-e-text--size-xl nova-legacy-e-text--family-display nova-legacy-e-text--spacing-none nova-legacy-e-text--color-grey-900 research-detail-header-section__title")
        article_name = article_name_element.text
    except AttributeError:
        article_name = "NotFound"
    # Find author name, profile, institute name and institute link
    article_author_list = []
    author_profile_list = []
    inst_list = []
    inst_link_list = []
    try:
        author_div = soup.find("div",
                               class_="nova-legacy-l-flex__item nova-legacy-l-flex nova-legacy-l-flex--gutter-m nova-legacy-l-flex--direction-column@s-up nova-legacy-l-flex--direction-row@m-up nova-legacy-l-flex--align-items-flex-start@s-up nova-legacy-l-flex--align-items-center@m-up nova-legacy-l-flex--justify-content-flex-start@s-up nova-legacy-l-flex--wrap-wrap@s-up research-detail-author-list__list js-authors-list")
        per_author_div = soup.find_all("div",
                                       class_="nova-legacy-l-flex__item research-detail-author-list__item research-detail-author-list__item--has-image")
        for author_div in per_author_div:
            author_profile_div = author_div.find("div",
                                                 class_="nova-legacy-e-text nova-legacy-e-text--size-m nova-legacy-e-text--family-display nova-legacy-e-text--spacing-none nova-legacy-e-text--color-inherit nova-legacy-v-person-list-item__title")
            author_element = author_profile_div.find("a",
                                                     class_="nova-legacy-e-link nova-legacy-e-link--color-inherit nova-legacy-e-link--theme-bare")
            article_author_list.append(author_element.getText())
            author_profile_list.append("https://www.researchgate.net/" + author_element.get("href"))

            try:
                inst_div = author_div.find("ul",
                                           class_="nova-legacy-e-list nova-legacy-e-list--size-m nova-legacy-e-list--type-inline nova-legacy-e-list--spacing-none nova-legacy-v-person-list-item__meta")
                inst_element = inst_div.find("span")
                inst_list.append(inst_element.getText())
                try:
                    inst_link = inst_element.find("a").get("href")
                    if inst_link != "false:":  # Sometimes the institute links are just mentioned as false in href
                        inst_link_list.append(inst_link)
                    else:
                        inst_link_list.append(" ")
                except AttributeError:  # if the institute has no link, then add a blank to the link list
                    inst_link_list.append(" ")
            except AttributeError:  # if author is not linked to any institute, then add a blank to the inst name & link
                inst_list.append(" ")
                inst_link_list.append(" ")
    except AttributeError:  # if no authors are found,then add a blank row to the csv file
        inst_list.append(" ")
        inst_link_list.append(" ")
        article_author_list.append(" ")
        author_profile_list.append(" ")
    # Zip all 4 lists into a tuple and add to csv
    author_inst_list = list(zip(article_author_list, author_profile_list, inst_list, inst_link_list))
    # Add a new row to csv for each article
    new_row = pd.Series({'Title': article_name,
                         'Author_Institution': author_inst_list
                         })
    df = pd.concat([df, new_row.to_frame().T], ignore_index=False)
    df.to_csv(f'{topic}.csv', index=False)
    i += 1
    print("Articles added to csv:", i)

# Save all final scraped data to a csv file
df.to_csv(f'{topic}.csv', index=False)

# Track time to improve speed
scrape_end_time = datetime.datetime.now()
scraping_time = scrape_end_time - start_time
print("Scraping speed for 100 articles: ", (scraping_time / nos) * 100)

# Get email id and prepare final excel
df = pd.read_csv(f"{topic}.csv")
df['Author_Institution'] = df['Author_Institution'].apply(lambda x: ast.literal_eval(x))  # Read string as list

clean_df = pd.DataFrame(columns=["Title", "Author", "Author_Profile", "Institute", "Institute_Link", "Website", "Email"])

e = 0
for n in range(len(df)):
    if df["Title"][n] != "NotFound":
        article_title = df["Title"][n]
        for a in range(len(df["Author_Institution"][n])):
            author = df["Author_Institution"][n][a][0]
            author_profile = df["Author_Institution"][n][a][1]
            institute = df["Author_Institution"][n][a][2]
            institute_link = df["Author_Institution"][n][a][3]
            email_finder = EmailFinder()  # Call email finder object to get email id from name and domain
            email_finder.get_email(author, institute_link)
            time.sleep(1)
            email = email_finder.email_id
            website = email_finder.website

            new_row = pd.Series({'Title': article_title,
                                 'Author': author,
                                 'Author_Profile': author_profile,
                                 'Institute': institute,
                                 'Institute_Link': institute_link,
                                 'Website': website,
                                 'Email': email
                                 })
            clean_df = pd.concat([clean_df, new_row.to_frame().T], ignore_index=False)
            e += 1
            print("Number of email id updated: ", e)

        with pd.ExcelWriter(f'{topic}.xlsx') as article_info:
            clean_df.to_excel(article_info, index=False)

email_find_time = datetime.datetime.now() - scrape_end_time
print("Scraping time for 100 emails: ", ((email_find_time / len(clean_df)) * 100))
