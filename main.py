import requests
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import os
import aisuite as ai
import json

# 导入 .env 中的信息
load_dotenv('.env')
OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY')
SENDER_ADDRESS: str = os.getenv('SENDER_ADDRESS')
SENDER_PASS: str = os.getenv('SENDER_PASS')
RECIPIENT_ADDRESS: str = os.getenv('RECIPIENT_ADDRESS')

# 定义主题列表
with open('theme.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
topics = [theme['title'] for theme in data['themes']]

# 初始化aisuite客户端
client = ai.Client()
# 调用 aisuite API 生成完整对话
def call_api_to_generate_dialog(topic, dialog_length):

    # 构造 API 请求数据
    messages = [
        {"role": "system", "content": "你是一个对话生成器，负责生成自然且有趣的对话内容。"},
        {
            "role": "user",
            "content":
                       f"请你以两个中国男生日常聊天的场合生成6段聊天对话，主题：{topic}；对话长度为 {dialog_length} 句"
                       f"这六段话需要尽可能保证场景不同，主题不同，情感不同，不要提供解决方案，可以是正向的结果的也可以是反向的结果，结尾不一定是happy ending, 但是不能走极端，可以只进行情感交流，增加一些负面情感。"
                       f"用词请尽量日常，且对话用语自然，符合日常聊天，意见并不一定要统一"
                       f"要求每句前有情绪提示词，以“A”“B”代指对话双方，情绪提示词请和对话语句位于同一行，紧跟放在“A”“B”的身份提示词之后"
                       f"每段对话具体的主题由你决定"
                       f"最后，需要在对话中引入情感聊天的内容，可以引起双方的情感共鸣"
                       f"重点体现这些情绪：{'Anxiety', 'Alertness', 'Sadness', 'Pride','Disgust', 'Anger', 'Guilt', 'Fear','Offense', 'Contempt'}"
                       f"请一定注意！在输出的时候把情绪此翻译成中文，格式上只保留每一段大标题，不要有其他的小标题，请一定注意！正文对话和对话不要有空行 参考格式如下：第一段：xxxxxxxx A【情绪】：xxxxxxxxxxxx B【情绪】：xxxxxxxxxxxx A【情绪】：xxxxxxxxxxxx B【情绪】：xxxxxxxxxxxx …… 谢谢您！"
        }
    ]

    try:
        # 选择模型(可选择"openai:gpt-4o", "anthropic:claude-3-5-sonnet-20240620"等)
        model = "anthropic:claude-3-5-sonnet-20240620"
        # 调用API生成对话
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.75,
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "（API调用失败，没有返回结果）"
    except Exception as e:
        return f"（API调用失败：{e}）"

# 批量生成多个话题的对话并保存到文件
def generate_all_dialogs(topics, dialog_length):
    # 获取当前日期时间
    timestamp = datetime.now().strftime("%m-%d-%H-%M")  # 文件名格式：月-日-时-分
    filename = f"dialogs_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        for idx, topic in enumerate(topics):
            print(f"正在生成第 {idx + 1} 个话题：{topic} 的对话...")
            dialog = call_api_to_generate_dialog(topic, dialog_length)
            file.write(f"第{idx + 1}个话题：{topic}\n{dialog}\n\n")

    print(f"所有对话已保存到文件：{filename}")
    return filename


# 使用 Gmail 发送邮件
def sendMail(mail_content, recv_address):
    message = MIMEMultipart()
    message['From'] = SENDER_ADDRESS
    message['To'] = recv_address
    message['Subject'] = '自动生成的对话合集'  # 邮件主题
    message.attach(MIMEText(mail_content, 'plain'))
    
    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()  # 启用 TLS 加密
        session.login(SENDER_ADDRESS, SENDER_PASS)
        session.sendmail(SENDER_ADDRESS, recv_address, message.as_string())
        session.quit()
        print(f"邮件发送成功！已发送到 {recv_address}")
    except Exception as e:
        print(f"邮件发送失败：{e}")

# 主函数
if __name__ == "__main__":
    # 生成对话并保存
    print("开始生成对话...")
    filename = generate_all_dialogs(topics, 14)

    # 读取文件内容并发送邮件
    with open("filename", "r", encoding="utf-8") as file:
        mail_content = file.read()
    print("开始发送邮件...")
    sendMail(mail_content, RECIPIENT_ADDRESS)
