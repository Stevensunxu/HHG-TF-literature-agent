from fpdf import FPDF
from datetime import datetime


class PDFReport(FPDF):

    def header(self):

        self.set_font(
            "Noto",
            size=14
        )

        self.cell(
            0,
            10,
            "Strong-field Ultrafast Literature Report",
            ln=True,
            align="C"
        )



def create_pdf(
        important,
        related,
        filename
):


    pdf=PDFReport()


    # 加载中文字体
    pdf.add_font(
        "Noto",
        "",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    )


    pdf.set_font(
        "Noto",
        size=11
    )


    pdf.add_page()


    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )


    today=datetime.now().strftime(
        "%Y-%m-%d"
    )


    pdf.multi_cell(
        0,
        8,
        f"""
强场超快光学文献报告

日期：
{today}


研究方向：

固体高次谐波 HHG

光学太赫兹发射

强场电子动力学

固体光场调控


"""
    )


    pdf.set_font(
        "Noto",
        size=12
    )


    pdf.cell(
        0,
        10,
        "一、重点推荐论文",
        ln=True
    )


    pdf.set_font(
        "Noto",
        size=10
    )


    for i,p in enumerate(important):


        text=f"""

{i+1}. {p['title']}


链接：

{p['link']}


中文总结：

{p['analysis']}



"""


        pdf.multi_cell(
            0,
            7,
            text
        )



    pdf.cell(
        0,
        10,
        "二、其他相关论文",
        ln=True
    )



    for p in related:


        text=f"""

{p['title']}

链接：

{p['link']}


方向：

{p['category']}


"""


        pdf.multi_cell(
            0,
            7,
            text
        )



    pdf.output(filename)
