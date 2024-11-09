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
import pytz  # 导入pytz库
import os
import pandas as pd


# 用于发送邮件的函数
def send_email(subject, body, to_email, attachment_path):
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
        server = smtplib.SMTP("smtp.126.com")  # 126邮件的SMTP服务器
        server.starttls()  # 启用TLS
        server.login(from_email, password)  # 登录
        server.sendmail(from_email, to_email, msg.as_string())  # 发送邮件
        logging.info("邮件发送成功！")
    except Exception as e:
        logging.info(f"发送邮件时出现错误: {e}")
    finally:
        if "server" in locals():  # 检查server是否已成功创建
            server.quit()  # 关闭服务器连接


# 获取数据并发送邮件的函数
def getWenCaiAndSendEmail():
    res = pywencai.get(
        query="人均持股市值>50万元；股东人数降序排序；近10日区间换手率<15%；流通市值大于100亿；股价在10日均线上方；持股人数小于15万；股价创近一年新高；总市值大于200亿；股价小于100元"
    )

    # 检查并创建 'data' 文件夹（如果不存在的话）
    if not os.path.exists("data"):
        os.makedirs("data")
    # 获取当前时间，并生成文件名
    current_datetime = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
    filename = "./data/" + current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx"
    countMap = getCount()
    if res is None or len(res) == 0:
        logging.info(f"没有任何数据 {current_datetime.strftime('%Y-%m-%d')}")
        return
    else:
        res.to_excel(filename)
        msg = ""
        for name in res["股票简称"]:
            print(name + str(countMap.get(name, 0)))
            msg += name + str(countMap.get(name, 0)) + ","

        # 将股票简称连接成字符串
        logging.info(f"发送邮件：{msg}")
        send_email("神股来了", msg, "panghui23@qq.com", f"./{filename}")


# 配置日志格式和级别
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("程序启动")


# 安排每周一到周五的晚上 6 点 18 分执行 getWenCaiAndSendEmail 函数
def schedule_job():
    # local_tz = pytz.timezone("Asia/Shanghai")
    # now = datetime.datetime.now(local_tz)
    # logging.info(f"当前时间: {now.strftime('%Y-%m-%d %H:%M')}")  # 输出当前时间

    # # 检查是否是周一到周五的18:18
    # if now.weekday() <= 5 and now.hour == 18 and now.minute == 18:
    getWenCaiAndSendEmail()


def getCount():
    folder_path = os.path.join(os.getcwd(), "data")  # 这里替换为你的文件夹路径
    # print(folder_path)
    # 获取所有 CSV 文件的路径
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]
    # print(csv_files)
    # 读取所有 CSV 文件并将它们存入一个列表中
    dataframes = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_excel(file_path)
        dataframes.append(df)

    # 如果需要，你可以将所有 DataFrame 合并为一个 DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)

    print(combined_df["股票简称"].value_counts())
    return combined_df["股票简称"].value_counts()


# 定义定时任务的时间
schedule.every().monday.at("15:18").do(schedule_job)
schedule.every().tuesday.at("15:18").do(schedule_job)
schedule.every().wednesday.at("15:18").do(schedule_job)
schedule.every().thursday.at("15:18").do(schedule_job)
schedule.every().friday.at("15:18").do(schedule_job)
# schedule.every().saturday.at("17:21").do(schedule_job)

# 设置每分钟检查一次
# schedule.every().minute.do(schedule_job)
# 每分钟检查一次
# 保持运行状态
# getWenCaiAndSendEmail()
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
