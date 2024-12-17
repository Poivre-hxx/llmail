import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# 导入 .env 中的信息
load_dotenv('.env')

def call_ollama(messages, model="qwen:2.5", temperature=0.7):
    """调用本地Ollama服务的通用函数"""
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查HTTP错误
        result = response.json()
        return result["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"调用Ollama服务出错: {e}")
        return None

def generate_game_prompt(user_prompt):
    """根据用户输入的游戏idea,生成详实的游戏prompt"""
    messages = [
        {"role": "system", "content": "你是一个游戏设计师助手,负责根据用户提供的游戏idea,生成详实的游戏设计文档。"},
        {"role": "user", "content": f"我的游戏idea是:{user_prompt},请你帮我丰富和填充这个idea,输出一个更加详实的游戏设计prompt。"}
    ]
    
    response = call_ollama(messages, temperature=0.7)
    return response if response else "游戏prompt生成失败,没有返回结果。"

def generate_game_code(game_prompt):
    """根据详实的游戏prompt,生成对应的Python游戏代码"""
    messages = [
        {"role": "system", "content": "你是一个游戏开发工程师,负责根据游戏设计文档,编写对应的Python游戏代码。"},
        {"role": "user", "content": f"游戏设计prompt:{game_prompt},请你根据这个prompt,用Python编写一个简单的游戏Demo。"}
    ]
    
    response = call_ollama(messages, temperature=0.2)
    return response if response else "游戏代码生成失败,没有返回结果。"

def main():
    print("欢迎使用游戏生成器!")
    
    while True:
        user_prompt = input("请输入您的游戏idea(输入q退出):")
        if user_prompt.lower() == 'q':
            print("感谢使用,再见!")
            break
        
        print("正在根据您的idea生成详实的游戏prompt...")
        game_prompt = generate_game_prompt(user_prompt)
        print(f"生成的游戏prompt如下:\n{game_prompt}")
        
        satisfied = input("您对这个game_prompt满意吗?(y/n)")
        if satisfied.lower() == 'y':
            print("正在根据game_prompt生成Python游戏代码...")
            game_code = generate_game_code(game_prompt)
            print(f"生成的游戏代码如下:\n{game_code}")
            
            filename = f"game_{datetime.now().strftime('%m%d%H%M%S')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(game_code)
            print(f"游戏代码已保存至:{filename}")
        else:
            print("好的,让我们重新开始。")

if __name__ == "__main__":
    main()