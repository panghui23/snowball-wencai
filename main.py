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
from config import config


# 用于发送邮件的函数
def send_email(subject, body, to_email, attachment_path):
    from_email = config.email_config.email
    password = config.email_config.password  # 发送者邮箱密码

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
def getWenCaiAndSendEmail(wencaiQuery):
    logging.info(f"读取问财结果{wencaiQuery}")
    res = pywencai.get(query=wencaiQuery)

    # 检查并创建 'data' 文件夹（如果不存在的话）
    if not os.path.exists("data"):
        os.makedirs("data")
    # 获取当前时间，并生成文件名
    current_datetime = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
    filename = "./data/" + current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx"
    countMap = getCount()
    if res is None or len(res) == 0:
        logging.info(f"没有任何问财股票 {current_datetime.strftime('%Y-%m-%d')}")
        return
    else:
        res.to_excel(filename)
        msg = ""
        for name in res["股票简称"]:
            print(name + str(countMap.get(name, 0)))
            msg += name + str(countMap.get(name, 0)) + ","

        # 将股票简称连接成字符串
        logging.info(f"发送邮件：{msg}")
        for email in config.receive_email:
            send_email("神股来了", msg, email, f"./{filename}")


def schedule_job():
    # 读取配置表问财查询条件
    for wencaiQuery in config.wencai_query:
        getWenCaiAndSendEmail(wencaiQuery)


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


# getWenCaiAndSendEmail()
if __name__ == "__main__":
    # 配置日志格式和级别
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("程序启动")
    # 从配置文件中获取时间
    execution_time: time = config.execution_time
    # 格式化为字符串格式 "HH:MM"
    time_str = execution_time.strftime("%H:%M")
    # 定义定时任务的时间
    schedule.every().monday.at(time_str).do(schedule_job)
    schedule.every().tuesday.at(time_str).do(schedule_job)
    schedule.every().wednesday.at(time_str).do(schedule_job)
    schedule.every().thursday.at(time_str).do(schedule_job)
    schedule.every().friday.at(time_str).do(schedule_job)
    print(f"主邮箱: {config.email_config.email}")
    print(f"接收邮箱: {config.receive_email}")
    print(f"问财查询条件: {config.wencai_query}")
    print(f"execution_time: {time_str}")
    # schedule_job()
    while True:
        schedule.run_pending()
        time.sleep(10)
