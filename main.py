import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime


# =========================
# 邮箱设置
# =========================

receiver = "sunxufs@163.com"

smtp_server = "smtp.163.com"
smtp_port = 465

# 从 GitHub Secrets 获取
password = os.environ["SMTP_PASSWORD"]


# =========================
# 测试邮件内容
# =========================

today = datetime.now().strftime("%Y-%m-%d")

content = f"""
HHG Literature Agent 测试邮件

日期:
{today}

如果你收到这封邮件，
说明：

✓ GitHub Actions 正常运行
✓ Python 正常执行
✓ 163 SMTP配置成功

下一步将加入：

- arXiv论文搜索
- 固体HHG筛选
- THz相关论文
- AI摘要分析

"""


msg = MIMEText(
    content,
    "plain",
    "utf-8"
)

msg["From"] = "sunxufs@163.com"
msg["To"] = receiver

msg["Subject"] = Header(
    "HHG Literature Agent Test",
    "utf-8"
)


# =========================
# 发送
# =========================

server = smtplib.SMTP_SSL(
    smtp_server,
    smtp_port
)

server.login(
    "sunxufs@163.com",
    password
)

server.sendmail(
    "sunxufs@163.com",
    receiver,
    msg.as_string()
)

server.quit()


print("Email sent successfully!")
