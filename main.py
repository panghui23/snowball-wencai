import pywencai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time
import datetime
import logging


# snowball1688@126.com   Aa2120212.
def send_email(subject, body, to_email, attachment_path):
    # 邮件发送者的邮箱和密码
    from_email = "snowball1688@126.com"  # 发送者邮箱
    password = "NKSLFbA3eghYqHUC"  # 发送者邮箱密码

    # 创建一个多部分邮件
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, "plain"))
    # 添加附件
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)  # 对附件进行编码
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_path.split('/')[-1]}",
            )
            msg.attach(part)  # 将附件添加到邮件中
    except Exception as e:
        logging.info(f"添加附件时出现错误: {e}")
        return
    try:
        # 连接到SMTP服务器并发送邮件
        server = smtplib.SMTP("smtp.126.com")  # Gmail SMTP服务器
        server.starttls()  # 启用TLS
        server.login(from_email, password)  # 登录
        server.sendmail(from_email, to_email, msg.as_string())  # 发送邮件
        logging.info("邮件发送成功！")
    except Exception as e:
        logging.info(f"发送邮件时出现错误: {e}")
    finally:
        if server:  # 检查server是否已成功创建
            server.quit()  # 关闭服务器连接


def getWenCaiAndSendEmail():
    res = pywencai.get(
        # query="人均持股市值>50万元；股东人数降序排序；近10日区间换手率<15%；流通市值大于100亿；股价在10日均线上方；持股人数小于15万；总市值大于200亿；股价小于100元"
        query="人均持股市值>50万元；股东人数降序排序；近10日区间换手率<15%；流通市值大于100亿；股价在10日均线上方；持股人数小于15万；股价创近一年新高；总市值大于200亿；股价小于100元"
        # query="人均持股市值>50万元；股东人数降序排序；近10日区间换手率<15%；流通市值大于1000亿；股价在10日均线上方；持股人数小于15万；股价创近一年新高；总市值大于200亿；股价小于100元"
    )
    current_datetime = datetime.datetime.now()
    now = current_datetime.strftime("%Y-%m-%d")
    # 格式化文件名（例如：2024-10-20_15-30-45.txt）
    filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx"
    if res is None:
        logging.info(f"no any data{now}")
        return
    else:
        res.to_excel(filename)
        msg = ""
        for r in res["股票简称"]:
            msg = msg + r + ","
        # msg = str(res["股票简称"])

        # 示例日志输出
        logging.info(f"发送邮件：{msg}")
        send_email("神股来了", msg, "panghui23@qq.com", "./" + filename)


# 配置日志格式和级别
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# 示例日志输出
logging.info("程序启动")

# getWenCaiAndSendEmail()


# 安排每周一到周五的晚上 6 点 18 分执行 log_message 函数
schedule.every().monday.at("18:18").do(getWenCaiAndSendEmail)
schedule.every().tuesday.at("18:18").do(getWenCaiAndSendEmail)
schedule.every().wednesday.at("18:18").do(getWenCaiAndSendEmail)
schedule.every().thursday.at("18:18").do(getWenCaiAndSendEmail)
schedule.every().friday.at("18:18").do(getWenCaiAndSendEmail)

while True:
    # 示例日志输出

    schedule.run_pending()
    time.sleep(1)
