from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from datetime import datetime



# 注册中文字体

pdfmetrics.registerFont(
    UnicodeCIDFont(
        "STSong-Light"
    )
)



def create_pdf(
        important,
        related,
        filename
):


    doc = SimpleDocTemplate(
        filename
    )


    styles=getSampleStyleSheet()


    chinese_style=ParagraphStyle(

        "Chinese",

        parent=styles["Normal"],

        fontName="STSong-Light",

        fontSize=10,

        leading=16

    )


    title_style=ParagraphStyle(

        "TitleCN",

        parent=styles["Title"],

        fontName="STSong-Light",

        fontSize=16

    )


    story=[]


    today=datetime.now().strftime(
        "%Y-%m-%d"
    )


    story.append(
        Paragraph(
            "强场超快光学文献报告",
            title_style
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            f"""
日期：{today}<br/>

研究方向：<br/>

固体高次谐波 HHG<br/>

光学太赫兹发射<br/>

强场电子动力学<br/>

固体光场调控
""",
            chinese_style
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            "一、重点推荐论文",
            title_style
        )
    )


    for i,p in enumerate(important):


        text=f"""

{i+1}. {p['title']}<br/><br/>

链接:<br/>
{p['link']}<br/><br/>


中文总结:<br/>

{p['analysis']}

"""


        story.append(
            Paragraph(
                text,
                chinese_style
            )
        )


        story.append(
            Spacer(1,15)
        )



    story.append(
        Paragraph(
            "二、其他相关论文",
            title_style
        )
    )


    data=[
        [
            "论文",
            "链接",
            "方向"
        ]
    ]


    for p in related:

        data.append(
            [
                p["title"],
                p["link"],
                p["category"]
            ]
        )


    table=Table(data)


    table.setStyle(
        TableStyle(
            [
                (
                "FONTNAME",
                (0,0),
                (-1,-1),
                "STSong-Light"
                )
            ]
        )
    )


    story.append(table)


    doc.build(
        story
    )
