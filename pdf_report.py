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

from reportlab.lib.pagesizes import A4


from datetime import datetime



# =========================
# 中文字体
# =========================

pdfmetrics.registerFont(
    UnicodeCIDFont(
        "STSong-Light"
    )
)



# =========================
# 生成PDF
# =========================

def create_pdf(
        important,
        related,
        filename
):


    doc = SimpleDocTemplate(

        filename,

        pagesize=A4,

        rightMargin=50,

        leftMargin=50,

        topMargin=50,

        bottomMargin=50

    )


    styles = getSampleStyleSheet()



    title_style = ParagraphStyle(

        "title_cn",

        parent=styles["Title"],

        fontName="STSong-Light",

        fontSize=16,

        leading=24

    )



    normal_style = ParagraphStyle(

        "normal_cn",

        parent=styles["Normal"],

        fontName="STSong-Light",

        fontSize=10,

        leading=16

    )



    small_style = ParagraphStyle(

        "small_cn",

        parent=styles["Normal"],

        fontName="STSong-Light",

        fontSize=8,

        leading=12

    )



    story=[]



    today=datetime.now().strftime(
        "%Y-%m-%d"
    )



    # =====================
    # 标题
    # =====================


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
日期：

{today}


研究方向：

固体高次谐波 HHG

光学太赫兹发射

强场电子动力学

固体光场调控


""",

            normal_style

        )

    )


    story.append(
        Spacer(1,20)
    )



    # =====================
    # 重点论文
    # =====================


    story.append(

        Paragraph(

            "一、重点推荐论文",

            title_style

        )

    )


    story.append(
        Spacer(1,15)
    )



    for i,p in enumerate(important):


        text=f"""

<b>{i+1}. {p['title']}</b>


来源期刊：

{p.get('source','Unknown')}


链接：

{p['link']}


中文总结：

{p['analysis']}


"""


        story.append(

            Paragraph(

                text,

                normal_style

            )

        )


        story.append(

            Spacer(1,20)

        )




    # =====================
    # 相关论文列表
    # =====================


    story.append(

        Paragraph(

            "二、其他相关论文",

            title_style

        )

    )


    story.append(
        Spacer(1,15)
    )



    table_data=[

        [

            "标题",

            "来源",

            "链接"

        ]

    ]



    for p in related:


        table_data.append(

            [

                p.get(
                    "title",
                    ""
                ),

                p.get(
                    "source",
                    ""
                ),

                p.get(
                    "link",
                    ""
                )

            ]

        )



    table=Table(

        table_data,

        repeatRows=1

    )



    table.setStyle(

        TableStyle(

            [

                (

                "FONTNAME",

                (0,0),

                (-1,-1),

                "STSong-Light"

                ),


                (

                "FONTSIZE",

                (0,0),

                (-1,-1),

                8

                ),


                (

                "VALIGN",

                (0,0),

                (-1,-1),

                "TOP"

                )

            ]

        )

    )


    story.append(table)



    doc.build(
        story
    )
