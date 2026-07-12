import os
import smtplib
import feedparser
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header

from openai import OpenAI


# ======================
# 邮箱
# ======================

EMAIL = "ttsunxust@163.com"

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


# ======================
# DeepSeek
# ======================

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)


# ======================
# 搜索关键词
# ======================

KEYWORDS = [

    "solid-state high harmonic generation",

    "high harmonic generation in solids",

    "strong-field ultrafast physics",

    "attosecond physics",

    "terahertz driven dynamics",

    "THz spectroscopy",

    "semiconductor Bloch equation",

    "TDDFT high harmonic generation",

    "Berry phase HHG",

    "MgO",

    "ZnO",

    "WS2",

    "MoS2"

]


# ======================
# arXiv搜索
# ======================


def search_arxiv():


    query = " OR ".join(
        [
            f'all:"{k}"'
            for k in KEYWORDS
        ]
    )


    params = {
    
        "search_query": query,
    
        "start": 0,
    
        "max_results": 30,
    
        "sortBy": "submittedDate",
    
        "sortOrder": "descending"
    
    }
    
    
    url = (
        "https://export.arxiv.org/api/query?"
        +
        urllib.parse.urlencode(params)
    )


    feed = feedparser.parse(url)


    papers=[]


    cutoff = datetime.now() - timedelta(days=3)


    for entry in feed.entries:


        date = datetime.strptime(
            entry.published[:10],
            "%Y-%m-%d"
        )


        if date < cutoff:
            continue


        papers.append(
            {
                "title":
                entry.title.replace("\n",""),

                "abstract":
                entry.summary.replace("\n"," "),

                "link":
                entry.link,

                "date":
                entry.published[:10]
            }
        )


    return papers



# ======================
# DeepSeek分析
# ======================


def analyze_with_ai(paper):


    prompt=f"""

You are an expert in strong-field solid-state physics.

Analyze this paper:

Title:
{paper['title']}


Abstract:
{paper['abstract']}


Evaluate:

1. Is this related to:
- solid HHG
- strong-field physics
- THz driven dynamics
- semiconductor Bloch equation
- TDDFT
- Berry phase


2. Give:

Relevance score (0-100)


3. Explain:

- Main physics mechanism
- Interband or intraband?
- Theoretical method
- Experimental method


4. Relation to my research:

I study:

- MgO solid HHG
- omega-2omega HHG
- THz controlled HHG
- SBE and TDDFT simulations


Return concise scientific comments.


"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"user",
                "content":prompt
            }

        ],

        temperature=0.2

    )


    return response.choices[0].message.content




# ======================
# 生成报告
# ======================


def generate_report(papers):


    report="""

HHG / Strong-field / THz Literature Report


"""


    analyzed=[]


    for p in papers:


        print(
            "Analyzing:",
            p["title"]
        )


        ai = analyze_with_ai(p)


        analyzed.append(
            {
                "title":p["title"],
                "link":p["link"],
                "date":p["date"],
                "ai":ai
            }
        )


    for i,p in enumerate(analyzed):


        report += f"""

========================

{i+1}. {p['title']}


Date:
{p['date']}


Link:
{p['link']}


AI Analysis:

{p['ai']}


"""


    return report



# ======================
# 发邮件
# ======================


def send_email(content):


    msg=MIMEText(
        content,
        "plain",
        "utf-8"
    )


    msg["From"]=EMAIL
    msg["To"]=EMAIL

    msg["Subject"]=Header(
        "HHG Literature AI Report",
        "utf-8"
    )


    server=smtplib.SMTP_SSL(
        SMTP_SERVER,
        SMTP_PORT
    )


    server.login(
        EMAIL,
        SMTP_PASSWORD
    )


    server.sendmail(
        EMAIL,
        EMAIL,
        msg.as_string()
    )


    server.quit()



# ======================
# main
# ======================


if __name__=="__main__":


    papers = search_arxiv()


    print(
        "Found papers:",
        len(papers)
    )


    if len(papers)==0:

        report="No papers found."

    else:

        report=generate_report(
            papers[:10]
        )


    send_email(report)


    print(
        "Done!"
    )
