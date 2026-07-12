import os
import smtplib
import urllib.parse
import feedparser


from datetime import datetime,timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


from openai import OpenAI

from pdf_report import create_pdf



EMAIL="ttsunxust@163.com"


SMTP_PASSWORD=os.environ["SMTP_PASSWORD"]



client=OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)



KEYWORDS=[


"solid-state high harmonic generation",

"high harmonic generation in solids",

"solid HHG",

"strong-field physics",

"strong-field electron dynamics",


"ultrafast terahertz emission",

"THz emission",

"optical rectification",

"photocurrent terahertz",


"light-field control",

"two-color excitation",

"omega-2omega",

"coherent control",


"ultrafast carrier dynamics",

"electron dynamics",

"carrier acceleration",


"semiconductor Bloch equation",

"TDDFT",

"Wannier",

"Berry connection"


]



def search_arxiv():


    query=" OR ".join(
        [
            f'all:"{x}"'
            for x in KEYWORDS
        ]
    )


    params={

        "search_query":query,

        "start":0,

        "max_results":50,

        "sortBy":"submittedDate",

        "sortOrder":"descending"

    }


    url=(
        "https://export.arxiv.org/api/query?"
        +
        urllib.parse.urlencode(params)
    )


    feed=feedparser.parse(url)


    papers=[]


    cutoff=datetime.utcnow()-timedelta(days=7)


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
            e.link

        })


    return papers



def score(p):


    text=(
        p["title"]
        +
        p["abstract"]
    ).lower()


    s=0


    keys={

    "high harmonic":30,

    "hhg":30,

    "strong-field":20,

    "terahertz emission":25,

    "optical rectification":20,

    "ultrafast":15,

    "semiconductor bloch":15,

    "tddft":10,


    }


    bad={

    "communication":-50,

    "wireless":-50,

    "network":-30,

    "antenna":-30,

    }


    for k,v in keys.items():

        if k in text:
            s+=v


    for k,v in bad.items():

        if k in text:
            s+=v


    return s




def deepseek_summary(p):


    prompt=f"""

你是强场超快凝聚态物理专家。


分析论文：

标题:
{p['title']}


摘要:
{p['abstract']}



要求：

用中文总结：

1. 研究问题

2. 核心物理机制

3. 主要实验或理论方法

4. 对强场HHG、光学THz发射、超快动力学有什么意义


不要评价推荐等级。

不要讨论是否使用SBE等。


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
        "今日文献报告已生成，请查看PDF附件。",
        "plain",
        "utf-8")
    )


    with open(
        pdf,
        "rb"
    ) as f:

        from email.mime.application import MIMEApplication

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




if __name__=="__main__":


    papers=search_arxiv()


    papers=sorted(
        papers,
        key=score,
        reverse=True
    )


    important=papers[:5]

    related=papers[5:15]



    for p in important:

        p["analysis"]=deepseek_summary(p)



    for p in related:

        p["category"]="相关方向"



    filename="Strong_Field_Ultrafast_Report.pdf"


    create_pdf(
        important,
        related,
        filename
    )


    send_mail(filename)


    print("Report finished")
