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
# 配置
# ==================================================

EMAIL = "ttsunxust@163.com"

SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)



# ==================================================
# 研究方向关键词
# ==================================================

KEYWORDS = [

    # 固体HHG
    "solid-state high harmonic generation",
    "high harmonic generation in solids",
    "solid HHG",
    "crystal HHG",

    # 强场
    "strong field physics",
    "strong-field electron dynamics",
    "nonlinear optical response",

    # THz光学
    "terahertz emission",
    "THz emission",
    "ultrafast terahertz generation",
    "optical rectification",
    "photocurrent THz",

    # 光场调控
    "light-field control",
    "field-driven solids",
    "two-color excitation",
    "omega-2omega",
    "Floquet engineering",

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


    query=" OR ".join(
        [
            f'all:"{k}"'
            for k in KEYWORDS
        ]
    )


    params={

        "search_query":query,
        "start":0,
        "max_results":40,
        "sortBy":"submittedDate",
        "sortOrder":"descending"

    }


    url="https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)


    feed=feedparser.parse(url)


    papers=[]


    cutoff=datetime.utcnow()-timedelta(days=14)


    for e in feed.entries:


        date=datetime.strptime(
            e.published[:10],
            "%Y-%m-%d"
        )


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
# Crossref
# ==================================================

def search_crossref():


    papers=[]


    for keyword in KEYWORDS[:10]:


        url="https://api.crossref.org/works"


        params={

            "query.title":keyword,

            "rows":5

        }


        try:

            r=requests.get(
                url,
                params=params,
                timeout=10
            )

            data=r.json()


        except:

            continue



        for item in data["message"]["items"]:


            title=item.get(
                "title",
                [""]
            )[0]


            doi=item.get(
                "DOI",
                ""
            )


            if title:


                papers.append({

                    "title":title,

                    "abstract":
                    item.get(
                        "abstract",
                        ""
                    ),

                    "link":
                    "https://doi.org/"+doi,

                    "source":
                    "Crossref"

                })


    return papers



# ==================================================
# Semantic Scholar
# ==================================================

def search_semantic():


    papers=[]


    queries=[

        "solid state high harmonic generation",

        "ultrafast terahertz emission",

        "strong field physics"

    ]


    for q in queries:


        try:

            r=requests.get(

                "https://api.semanticscholar.org/graph/v1/paper/search",

                params={

                    "query":q,

                    "limit":10,

                    "fields":
                    "title,abstract,url"

                },

                timeout=10

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
                "Semantic Scholar"

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
# 关键词评分
# ==================================================
# ==================================================
# 期刊等级评分
# ==================================================

def journal_score(paper):


    text = (

        paper["title"]

        +

        paper.get("abstract","")

        +

        paper.get("source","")

    ).lower()


    score = 0


    journals = {


        # Nature系列

        "nature physics":50,

        "nature photonics":50,

        "nature":45,

        "nature communications":35,


        # Science系列

        "science":45,

        "science advances":35,


        # APS

        "physical review letters":40,

        "phys. rev. lett":40,

        "prl":40,


        "physical review x":45,


        "physical review b":25,

        "phys. rev. b":25,


        # Optics

        "optica":35,

        "optics letters":20,

        "advanced photonics":35,


        # 其他强相关

        "light: science & applications":40,

        "laser & photonics reviews":35,


        # 超快

        "ultrafast science":35,

        "acs photonics":30,


    }


    for j,w in journals.items():

        if j in text:

            score += w


    return score
    
def score(p):


    text=(

        p["title"]

        +

        p["abstract"]

    ).lower()


    s=0


    high={


        "high harmonic":30,

        "hhg":30,

        "strong-field":20,

        "terahertz emission":25,

        "ultrafast":15,

        "optical rectification":20,

        "carrier dynamics":15,

        "semiconductor bloch":15,

        "tddft":10

    }



    bad={


        "communication":-50,

        "wireless":-50,

        "antenna":-40,

        "network":-30

    }



    for k,v in high.items():

        if k in text:

            s+=v



    for k,v in bad.items():

        if k in text:

            s+=v



    return s




# ==================================================
# DeepSeek中文总结
# ==================================================

def analyze(paper):


    prompt=f"""

你是强场超快凝聚态物理专家。


论文：

{paper['title']}


摘要：

{paper['abstract']}



请用中文写一个科研摘要。


包括：

1. 研究内容

2. 核心物理机制

3. 实验或理论方法

4. 对以下方向的意义：

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
# 邮件
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
            "本周强场超快文献PDF报告已生成。",
            "plain",
            "utf-8"
        )
    )


    with open(pdf,"rb") as f:

        att=MIMEApplication(f.read())


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


    print("Searching...")


    papers=[]


    papers += search_arxiv()

    papers += search_crossref()

    papers += search_semantic()



    papers=remove_duplicate(papers)


    print(
        "Total papers:",
        len(papers)
    )


    papers=sorted(
    
        papers,
    
        key=lambda x:
    
            score(x)
    
            +
    
            journal_score(x),
    
        reverse=True
    
    )


    important=papers[:5]

    related=papers[5:15]



    for p in important:


        print(
            "AI:",
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


    print("Finished")
