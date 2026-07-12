import os
import smtplib
import urllib.request
import urllib.parse
import feedparser

from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timedelta


# =====================
# 配置
# =====================

EMAIL = "ttsunxust@163.com"

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

PASSWORD = os.environ["SMTP_PASSWORD"]


KEYWORDS = [
    "solid-state high harmonic generation",
    "high harmonic generation in solids",
    "strong-field ultrafast",
    "terahertz dynamics",
    "THz spectroscopy",
    "semiconductor Bloch equation",
    "TDDFT HHG",
    "Berry phase HHG",
    "MgO",
    "ZnO",
    "WS2"
]


# =====================
# 搜索arXiv
# =====================

def search_arxiv():

    query = " OR ".join(
        ['all:"{}"'.format(k)
         for k in KEYWORDS]
    )


    url = (
        "https://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {
                "search_query": query,
                "start":0,
                "max_results":20,
                "sortBy":"submittedDate",
                "sortOrder":"descending"
            }
        )
    )


    data = urllib.request.urlopen(url).read()

    feed = feedparser.parse(data)


    papers=[]

    cutoff = datetime.now() - timedelta(days=3)


    for entry in feed.entries:

        title = entry.title.replace("\n","")

        summary = entry.summary.replace("\n"," ")

        date = entry.published[:10]


        papers.append(
            {
                "title":title,
                "date":date,
                "summary":summary,
                "link":entry.link
            }
        )


    return papers



# =====================
# 生成邮件
# =====================

def generate_report(papers):

    today=datetime.now().strftime("%Y-%m-%d")


    text=f"""
HHG / Strong-field / THz Literature Test

Date:
{today}

Recent papers:

"""


    if len(papers)==0:

        text+="No related papers found."

    else:

        for i,p in enumerate(papers[:10]):

            text+=f"""

----------------------

{i+1}. {p['title']}

Date:
{p['date']}

Link:
{p['link']}


Abstract:

{p['summary'][:800]}


"""


    return text



# =====================
# 发邮件
# =====================

def send_mail(content):


    msg=MIMEText(
        content,
        "plain",
        "utf-8"
    )


    msg["From"]=EMAIL
    msg["To"]=EMAIL

    msg["Subject"]=Header(
        "HHG Literature Test",
        "utf-8"
    )


    server=smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT
    )


    server.login(
        EMAIL,
        PASSWORD
    )


    server.sendmail(
        EMAIL,
        EMAIL,
        msg.as_string()
    )


    server.quit()



if __name__=="__main__":


    papers=search_arxiv()

    report=generate_report(papers)

    send_mail(report)

    print(
        "Literature report sent!"
    )
