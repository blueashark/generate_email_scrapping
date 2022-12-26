import pandas as pd
import ast
import openpyxl
from email_finder import EmailFinder

# Enter the topic manually, it should match the topic from main.py file
topic = "covid_19"

df = pd.read_csv(f"{topic}.csv")
df['Author_Institution'] = df['Author_Institution'].apply(lambda x: ast.literal_eval(x))

clean_df = pd.DataFrame(columns=["Title", "Author", "Institute", "Email"])

for n in range(len(df)):
    article_title = df["Title"][n]
    for a in range(len(df["Author_Institution"][n])):
        author = df["Author_Institution"][n][a][0]
        institute = df["Author_Institution"][n][a][1]
        email_finder = EmailFinder()
        email_finder.get_email(df["Author_Institution"][n][a][0], df["Author_Institution"][n][a][1])
        email = email_finder.email_id

        new_row = pd.Series({'Title': article_title,
                             'Author': author,
                             'Institute': institute,
                             'Email': email
                             })
        clean_df = pd.concat([clean_df, new_row.to_frame().T], ignore_index=False)

with pd.ExcelWriter(f'{topic}.xlsx') as article_info:
    clean_df.to_excel(article_info, index=False)

