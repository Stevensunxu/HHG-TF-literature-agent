import os
import smtplib
import urllib.parse
import feedparser

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header

from openai import OpenAI


# ==================================================
# 邮件配置
# ==================================================

EMAIL = "ttsunxust@163.com"

SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


# ==================================================
# DeepSeek
# ==================================================

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)


# ==================================================
# 研究关键词
# ==================================================

KEYWORDS = [

    # 固体HHG
    "solid-state high harmonic generation",
    "high harmonic generation in solids",
    "solid HHG",
    "crystal high harmonic generation",

    # 强场
    "strong-field physics",
    "strong-field electron dynamics",
    "nonperturbative response",

    # 光学THz
    "terahertz emission",
    "THz emission",
    "ultrafast terahertz generation",
    "laser-induced terahertz",
    "optical rectification",
    "photocurrent terahertz",

    # 光场控制
    "light-field control",
    "ultrafast control of solids",
    "two-color excitation",
    "omega-2omega",
    "coherent control",

    # 超快动力学
    "ultrafast carrier dynamics",
    "electron dynamics",
    "carrier acceleration",
    "Bloch oscillation",

    # 理论
    "semiconductor Bloch equation",
    "TDDFT",
    "Wannier",
    "Berry connection",
    "quantum geometry"

]


# ==================================================
# arXiv搜索
# ==================================================

def search_arxiv():


    query = " OR ".join(
        [
            f'all:"{x}"'
            for x in KEYWORDS
        ]
    )


    params = {

        "search_query": query,

        "start":0,

        "max_results":40,

        "sortBy":"submittedDate",

        "sortOrder":"descending"

    }


    url = (
        "https://export.arxiv.org/api/query?"
        +
        urllib.parse.urlencode(params)
    )


    print(url)


    feed = feedparser.parse(url)


    papers=[]


    cutoff = datetime.utcnow()-timedelta(days=7)


    for entry in feed.entries:


        try:

            date=datetime.strptime(
                entry.published[:10],
                "%Y-%m-%d"
            )

        except:

            continue


        if date < cutoff:
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



# ==================================================
# 关键词预评分
# ==================================================

def keyword_score(paper):


    text = (
        paper["title"]
        +
        paper["abstract"]
    ).lower()


    score=0


    positive={

        "high harmonic":30,

        "hhg":30,

        "strong-field":20,

        "terahertz emission":25,

        "thz emission":25,

        "optical rectification":20,

        "ultrafast":15,

        "carrier dynamics":15,

        "semiconductor bloch":15,

        "tddft":10,

        "berry":10

    }


    negative={

        "communication":-50,

        "wireless":-50,

        "antenna":-40,

        "network":-30,

        "cryptography":-50

    }


    for k,v in positive.items():

        if k in text:

            score += v


    for k,v in negative.items():

        if k in text:

            score += v


    return score



# ==================================================
# DeepSeek分析
# ==================================================

def ai_analysis(paper):


    prompt=f"""

你是一名强场超快凝聚态物理专家。


请分析下面论文。


标题:

{paper['title']}


摘要:

{paper['abstract']}



我的研究方向：

- 固体高次谐波 HHG
- MgO强场实验
- ω-2ω双色场HHG
- 光学THz发射
- THz调控固体电子动力学
- SBE
- TDDFT
- Wannier方法


请用中文回答：


1. 相关性评分（0-100）


2. 论文主要研究什么？


3. 关键物理机制：

讨论：

- interband贡献
- intraband贡献
- Berry phase/quantum geometry
- 载流子动力学
- 声子作用


4. 方法：

实验？
理论？

是否使用：

- SBE
- TDDFT
- Wannier


5. 与我的研究关系：

是否可能解释：

- MgO HHG
- 双色场增强
- THz调控
- 超快电子动力学


6. 推荐等级：

必须读 / 推荐读 / 低优先级


如果只是THz通信、THz网络、量子通信，请明确指出无关。


"""


    result=client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {

            "role":"user",

            "content":prompt

            }

        ],

        temperature=0.2

    )


    return result.choices[0].message.content



# ==================================================
# 生成中文邮件
# ==================================================

def generate_report(papers):


    today=datetime.now().strftime("%Y-%m-%d")


    report=f"""

================================================

强场超快光学文献日报

日期：
{today}


研究方向：

固体HHG | 光学THz发射 | 光场调控 | 超快动力学


================================================


"""


    if len(papers)==0:

        return report+"最近没有发现相关论文"



    # 取最高评分前10篇

    papers=sorted(

        papers,

        key=keyword_score,

        reverse=True

    )


    for i,p in enumerate(papers[:10]):


        print(
            "AI分析:",
            p["title"]
        )


        analysis=ai_analysis(p)


        report += f"""

------------------------------------------------


{i+1}. {p['title']}


日期：

{p['date']}


链接：

{p['link']}



DeepSeek分析：


{analysis}



"""


    return report



# ==================================================
# 发邮件
# ==================================================

def send_email(content):


    msg=MIMEText(

        content,

        "plain",

        "utf-8"

    )


    msg["From"]=EMAIL

    msg["To"]=EMAIL


    msg["Subject"]=Header(

        "强场超快光学文献日报",

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



# ==================================================
# MAIN
# ==================================================

if __name__=="__main__":


    print("开始搜索arXiv")


    papers=search_arxiv()


    print(
        "找到论文:",
        len(papers)
    )


    report=generate_report(
        papers
    )


    send_email(
        report
    )


    print("发送完成")
