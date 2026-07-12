import os
import smtplib
import urllib.parse
import feedparser

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header

from openai import OpenAI


# =====================================================
# 基础配置
# =====================================================

EMAIL = "ttsunxust@163.com"

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


# =====================================================
# DeepSeek API
# =====================================================

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)


# =====================================================
# 搜索关键词
# =====================================================

KEYWORDS = [

    "high harmonic generation",
    "solid HHG",
    "solid-state HHG",

    "strong field physics",
    "strong-field electron dynamics",

    "attosecond",
    "ultrafast electron dynamics",

    "semiconductor Bloch equation",
    "TDDFT",

    "Berry phase",
    "Berry curvature",
    "quantum geometry",

    "terahertz",
    "THz",

    "MgO",
    "ZnO",
    "WS2",
    "MoS2"

]


# 最近多少天
SEARCH_DAYS = 7



# =====================================================
# arXiv 搜索
# =====================================================

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


    print(url)


    feed = feedparser.parse(url)


    papers=[]


    cutoff = datetime.utcnow() - timedelta(days=SEARCH_DAYS)


    for entry in feed.entries:


        try:

            published=datetime.strptime(
                entry.published[:10],
                "%Y-%m-%d"
            )

        except:

            continue


        if published < cutoff:
            continue



        papers.append({

            "title":
            entry.title.replace("\n"," "),

            "abstract":
            entry.summary.replace("\n"," "),

            "date":
            entry.published[:10],

            "link":
            entry.link

        })


    return papers



# =====================================================
# DeepSeek 分析
# =====================================================


def analyze_paper(paper):


    prompt=f"""

You are an expert researcher in strong-field
solid-state physics and high harmonic generation.


Analyze this paper:


Title:
{paper['title']}


Abstract:
{paper['abstract']}



The user's research background:

- MgO solid-state HHG experiments
- omega-2omega two-color HHG
- THz controlled HHG
- semiconductor Bloch equation
- TDDFT simulations
- Wannier interpolation


Please provide:


1. Relevance score (0-100)


2. Main physics mechanism

Discuss:

- interband contribution
- intraband contribution
- Berry phase
- electron-hole dynamics
- phonon effects


3. Method:

Experiment / Theory

If theory:

SBE?
TDDFT?
Wannier?


4. Relation to MgO HHG:

Explain possible relevance.


5. Recommendation:

Must read / Worth reading / Low priority


Keep it concise.


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




# =====================================================
# 生成报告
# =====================================================


def generate_report(papers):


    today=datetime.now().strftime("%Y-%m-%d")


    report=f"""

================================================

HHG / Strong-field / THz Literature Report

Date:
{today}

Search period:
Last {SEARCH_DAYS} days


================================================


"""


    if len(papers)==0:

        return report + "\nNo related papers found."


    # 最多分析10篇

    for i,paper in enumerate(papers[:10]):


        print(
            "Analyzing:",
            paper["title"]
        )


        analysis=analyze_paper(
            paper
        )


        report += f"""

------------------------------------------------


{i+1}. {paper['title']}


Date:

{paper['date']}


arXiv:

{paper['link']}



DeepSeek Analysis:


{analysis}



"""


    return report




# =====================================================
# 邮件发送
# =====================================================


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



# =====================================================
# MAIN
# =====================================================


if __name__=="__main__":


    print("Searching arXiv...")


    papers=search_arxiv()


    print(
        "Found papers:",
        len(papers)
    )


    report=generate_report(
        papers
    )


    send_email(
        report
    )


    print(
        "DONE"
    )
