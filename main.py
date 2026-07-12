import os
import smtplib
import requests
import urllib.parse
import feedparser

from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header

from openai import OpenAI

from pdf_report import create_pdf



# ==================================================
# 基本配置
# ==================================================

EMAIL = "ttsunxust@163.com"

SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)



# ==================================================
# 研究关键词
# ==================================================

KEYWORDS = [

    # HHG
    "solid-state high harmonic generation",
    "high harmonic generation in solids",
    "solid HHG",
    "crystal HHG",

    # 强场
    "strong-field physics",
    "strong field electron dynamics",
    "nonlinear optical response",

    # THz 光学
    "terahertz emission",
    "THz emission",
    "ultrafast terahertz generation",
    "optical rectification",
    "photocurrent terahertz",

    # 光场调控
    "light-field control",
    "field-driven solids",
    "two-color excitation",
    "omega-2omega",
    "coherent control",

    # 超快动力学
    "ultrafast carrier dynamics",
    "electron dynamics",
    "carrier acceleration",

    # 理论
    "semiconductor Bloch equation",
    "TDDFT",
    "Berry phase",
    "quantum geometry"

]



# ==================================================
# arXiv
# ==================================================

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
        "max_results": 40,
        "sortBy": "submittedDate",
        "sortOrder": "descending"

    }


    url = (
        "https://export.arxiv.org/api/query?"
        +
        urllib.parse.urlencode(params)
    )


    feed = feedparser.parse(url)


    papers = []


    cutoff = datetime.utcnow() - timedelta(days=14)



    for e in feed.entries:


        try:

            date = datetime.strptime(
                e.published[:10],
                "%Y-%m-%d"
            )

        except:

            continue


        if date < cutoff:
            continue


        papers.append({

            "title":
            e.title.replace("\n"," "),

            "abstract":
            e.summary.replace("\n"," "),

            "link":
            e.link,

            "source":
            "arXiv"

        })


    return papers




# ==================================================
# Crossref 正式期刊
# ==================================================

def search_crossref():


    papers=[]


    for keyword in KEYWORDS[:10]:


        try:

            r=requests.get(

                "https://api.crossref.org/works",

                params={

                    "query.title":keyword,

                    "rows":10

                },

                timeout=15

            )


            data=r.json()


        except:

            continue



        for item in data["message"]["items"]:


            title=item.get(
                "title",
                [""]
            )[0]


            if not title:
                continue



            journal=item.get(
                "container-title",
                ["Unknown"]
            )[0]



            doi=item.get(
                "DOI",
                ""
            )


            abstract=item.get(
                "abstract",
                ""
            )


            papers.append({

                "title":title,

                "abstract":abstract,

                "link":
                "https://doi.org/"+doi,

                "source":journal

            })


    return papers




# ==================================================
# Semantic Scholar
# ==================================================

def search_semantic():


    papers=[]


    queries=[

        "solid state high harmonic generation",

        "strong field ultrafast physics",

        "optical terahertz emission"

    ]


    for q in queries:


        try:

            r=requests.get(

                "https://api.semanticscholar.org/graph/v1/paper/search",

                params={

                    "query":q,

                    "limit":10,

                    "fields":
                    "title,abstract,url,venue"

                },

                timeout=15

            )


            data=r.json()


        except:

            continue



        for p in data.get("data",[]):


            papers.append({

                "title":
                p.get("title",""),

                "abstract":
                p.get("abstract",""),

                "link":
                p.get("url",""),

                "source":
                p.get("venue","Semantic Scholar")

            })


    return papers




# ==================================================
# 去重
# ==================================================

def remove_duplicate(papers):


    result=[]

    seen=set()


    for p in papers:


        key=p["title"].lower().strip()


        if key not in seen:

            seen.add(key)

            result.append(p)


    return result




# ==================================================
# 物理相关性评分
# ==================================================

def physics_score(paper):


    text=(

        paper["title"]

        +

        paper.get("abstract","")

    ).lower()



    score=0



    keywords={


        "high harmonic":30,

        "hhg":30,

        "strong-field":20,

        "strong field":20,


        "terahertz emission":25,

        "thz emission":25,

        "optical rectification":20,


        "ultrafast":15,

        "carrier dynamics":15,


        "semiconductor bloch":15,

        "tddft":10,


        "berry":10,

        "quantum geometry":10,


        "two-color":15

    }



    for k,v in keywords.items():

        if k in text:

            score+=v



    bad={


        "communication":-50,

        "wireless":-50,

        "antenna":-40,

        "network":-40,

        "cryptography":-50

    }



    for k,v in bad.items():

        if k in text:

            score+=v



    return score




# ==================================================
# 期刊等级评分
# ==================================================

def journal_score(paper):


    text=(

        paper.get("source","")

        +

        paper["title"]

    ).lower()



    score=0



    journals={


        "nature physics":50,

        "nature photonics":50,

        "nature":45,

        "science":45,

        "science advances":35,


        "physical review letters":40,

        "phys. rev. lett":40,

        "prl":40,


        "physical review x":45,


        "physical review b":25,

        "phys. rev. b":25,


        "optica":35,

        "advanced photonics":35,

        "acs photonics":30,


        "light: science & applications":40,

        "ultrafast science":35

    }



    for j,v in journals.items():

        if j in text:

            score+=v



    return score




# ==================================================
# DeepSeek中文总结
# ==================================================

def analyze(paper):


    prompt=f"""

你是强场超快凝聚态物理专家。


论文标题：

{paper['title']}


摘要：

{paper['abstract']}



请用中文总结：

1. 研究内容

2. 核心物理机制

3. 实验或理论方法

4. 对以下方向意义：

- 固体HHG
- 光学THz发射
- 强场电子动力学
- 固体光场调控


不要输出评分。
不要输出推荐等级。


"""


    r=client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"user",
                "content":prompt
            }

        ],

        temperature=0.2

    )


    return r.choices[0].message.content




# ==================================================
# 邮件发送
# ==================================================

def send_mail(pdf):


    msg=MIMEMultipart()


    msg["From"]=EMAIL

    msg["To"]=EMAIL


    msg["Subject"]=Header(

        "强场超快光学文献报告",

        "utf-8"

    )


    msg.attach(

        MIMEText(

            "本周强场超快光学文献PDF报告见附件。",

            "plain",

            "utf-8"

        )

    )


    with open(pdf,"rb") as f:


        att=MIMEApplication(
            f.read()
        )


        att.add_header(

            "Content-Disposition",

            "attachment",

            filename=pdf

        )


        msg.attach(att)



    server=smtplib.SMTP_SSL(

        "smtp.163.com",

        465

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




# ==================================================
# MAIN
# ==================================================

if __name__=="__main__":


    print("开始搜索")


    papers=[]


    papers += search_arxiv()

    papers += search_crossref()

    papers += search_semantic()



    papers=remove_duplicate(
        papers
    )


    print(
        "论文数量:",
        len(papers)
    )



    papers=sorted(

        papers,

        key=lambda x:

        physics_score(x)
        +
        journal_score(x),

        reverse=True

    )



    important=papers[:5]


    related=papers[5:15]



    for p in important:


        print(
            "AI分析:",
            p["title"]
        )


        p["analysis"]=analyze(p)



    for p in related:

        p["category"]=p["source"]



    pdf="Strong_Field_Ultrafast_Report.pdf"



    create_pdf(

        important,

        related,

        pdf

    )



    send_mail(pdf)



    print("完成")
