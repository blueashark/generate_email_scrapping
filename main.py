import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ast
import openpyxl
from email_finder import EmailFinder

topic_dict = {
    "genomics": "https://www.researchgate.net/topic/Genomics/publications",
    "gene_expression": "https://www.researchgate.net/topic/Gene-Expression/publications",
    "gene_regulation": "https://www.researchgate.net/topic/Gene-Regulation/publications",
    "epigenetics": "https://www.researchgate.net/topic/Epigenetics/publications",
    "genetics": "https://www.researchgate.net/topic/Genetics/publications",
    "covid_19": "https://www.researchgate.net/topic/COVID-19/publications"
}

topic = input("Select a topic (covid_19/genetics/epigenetics/gene_regulation/gene_expression/genomics): ")
chromedriver_location = input("Enter the location of chromedriver on your pc (e.g./Users/satyaprakashsahoo/Documents/Chrome Driver/chromedriver): ")
nos = int(input("How many articles you want to search?: "))

# Create dataframe and empty csv to store all scrapped information
df = pd.DataFrame({'Title': [],
                   'Author_Institution': []
                   })
df.to_csv(f'{topic}.csv', index=False)

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

# Browse through each article link and get the required details. Store them in csv format.
for link in article_link_list[:nos]:
    driver.get(link)
    try:
        article_name_element = driver.find_element(By.XPATH, '//*[@id="lite-page"]/main/section/section[1]/div/div/h1')
        article_name = article_name_element.text
    except NoSuchElementException or TimeoutException:
        article_name = "NotFound"

    try:
        author_wi_elements = driver.find_elements(By.XPATH,
                                              '//*[@id="lite-page"]/main/section/section[1]/div/div/div[3]/div/div/div/div/div[2]/div/div/div/div/div/a')
        article_author_list = [author.get_property("text") for author in author_wi_elements]
        author_profile_list = [author.get_property("href") for author in author_wi_elements]
    except NoSuchElementException or TimeoutException:
        article_author_list = []
        author_profile_list = []

    try:
        inst_elements = driver.find_elements(By.XPATH,
                                             '//*[@id="lite-page"]/main/section/section[1]/div/div/div[3]/div/div/div/div/div[2]/div/div/div/div/ul/li/span/a')
        inst_list = [inst.get_property("text") for inst in inst_elements]
        inst_link_list = [inst.get_property("href") for inst in inst_elements]
    except NoSuchElementException or TimeoutException:
        inst_list = []
        inst_link_list = []

    author_inst_list = list(zip(article_author_list, author_profile_list, inst_list, inst_link_list))

    try:
        author_wo_elements = driver.find_elements(By.XPATH,
                                              '//*[@id="lite-page"]/main/section/section[1]/div/div/div[3]/div/div/div[1]/div/div/div[2]/div/div/div/div/div/a')
        for a in range(len(author_wo_elements)):
            author_inst_list.append((author_wo_elements[a].get_property("text"), author_wo_elements[a].get_property("href"), " ", " "))
    except NoSuchElementException or TimeoutException:
        None

    new_row = pd.Series({'Title': article_name,
                         'Author_Institution': author_inst_list
                         })
    df = pd.concat([df, new_row.to_frame().T], ignore_index=False)
    df.to_csv(f'{topic}.csv', index=False)
    time.sleep(5)

df.to_csv(f'{topic}.csv', index=False)

# Get email id and prepare final excel
df = pd.read_csv(f"{topic}.csv")
df['Author_Institution'] = df['Author_Institution'].apply(lambda x: ast.literal_eval(x))

clean_df = pd.DataFrame(columns=["Title", "Author", "Author_Profile", "Institute", "Institute_Link", "Website", "Email"])

for n in range(len(df)):
    article_title = df["Title"][n]
    for a in range(len(df["Author_Institution"][n])):
        author = df["Author_Institution"][n][a][0]
        author_profile = df["Author_Institution"][n][a][1]
        institute = df["Author_Institution"][n][a][2]
        institute_link = df["Author_Institution"][n][a][3]
        email_finder = EmailFinder()
        email_finder.get_email(author, institute_link)
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
        time.sleep(5)

with pd.ExcelWriter(f'{topic}.xlsx') as article_info:
    clean_df.to_excel(article_info, index=False)
