import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# 导入 .env 中的信息
load_dotenv('.env')

def call_ollama(messages, model="qwen2:7b", temperature=0.7):
    """调用本地Ollama服务的通用函数"""
    url = "http://localhost:11434/api/generate"
    
    # 将messages转换为prompt字符串
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"System: {msg['content']}\n"
        else:
            prompt += f"{msg['content']}\n"
    
    payload = {
        "model": model,
        "prompt": prompt,  # Ollama使用prompt而不是messages
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查HTTP错误
        result = response.json()
        
        # 打印响应内容以便调试
        print("\nAPI响应：", json.dumps(result, indent=2, ensure_ascii=False))
        
        # Ollama的响应中直接包含response字段
        if "response" in result:
            return result["response"]
        else:
            print("警告：响应中没有找到'response'字段")
            print("完整响应：", result)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"调用Ollama服务出错: {e}")
        return None
    except KeyError as e:
        print(f"解析响应时出错: {e}")
        print(f"收到的响应: {result}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None

def generate_game_prompt(user_prompt):
    """根据用户输入的游戏idea,生成详实的游戏prompt"""
    messages = [
        {"role": "system", "content": "你是一个游戏设计师助手,负责根据用户提供的游戏idea,丰富填充这个idea。"},
        {"role": "user", 
        "content": f"""
            1. 提供核心玩法和机制的清晰、简短描述（类似于经典迷你游戏规则）。
            2. 确保提示符已准备好 Python，重点关注游戏结构（例如，对象、控件、事件）。
            3. 包括简单易懂的定义的胜利和失败条件。
            4. 突出显示经典的游戏元素，例如得分、级别或挑战，同时保持简单性和可玩性。
            5. 强调可以直接转换为代码的基本规则、控件和交互。
            6. 只需考虑基本实现，而不必考虑诸如音效、材质纹理等问题。
            7. 考虑到 token 长度的限制，越精简越好，只保留游戏的必要的功能。"""
        }
    ]
    
    response = call_ollama(messages, temperature=0.7)
    return response if response else "游戏prompt生成失败,没有返回结果。"

def generate_game_code(game_prompt):
    """根据详实的游戏prompt,生成对应的Python游戏代码"""
    messages = [
        {"role": "system", "content": "你是一个游戏开发工程师,负责根据idea,编写对应的Python游戏代码。"},
        {"role": "user", "content": f"游戏设计prompt:{game_prompt},请你根据这个prompt,用Python编写一个简单的游戏Demo。"
                                    f"""需要满足如下要求
                                        1. 屏幕分辨率设置为 720x480 像素。
                                        2. 使用 Pygame 库实现所有游戏功能，包括图形渲染、事件处理、碰撞检测等。
                                        3. 游戏必须完全可玩，具备明确的开始和结束条件（例如：游戏胜利或失败的条件）。
                                        4. 游戏视觉效果应仅使用基本几何形状（如：三角形、圆形、正方形等）。
                                        5. 设计并实现一个游戏循环，确保事件处理（例如：用户输入、键盘按键等）正常工作，并实现基本的碰撞检测功能。
                                        6. 充分考虑所使用的库，确保调用完整
                                    """
        }
    ]                              

    
    response = call_ollama(messages, temperature=0.2)
    return response if response else "游戏代码生成失败,没有返回结果。"

def check_ollama_service():
    """检查Ollama服务是否可用"""
    try:
        response = requests.get("http://localhost:11434")
        return True
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到Ollama服务。请确保：")
        print("1. Ollama已经安装")
        print("2. Ollama服务正在运行（使用'ollama serve'启动）")
        print("3. 已经安装了所需的模型（使用'ollama pull qwen2:7b'安装）")
        return False

def main():
    print("欢迎使用游戏生成器!")
    
    # 首先检查服务是否可用
    if not check_ollama_service():
        return
    
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
            
            filename = f"game_ollamacn_{datetime.now().strftime('%m%d%H%M%S')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(game_code)
            print(f"游戏代码已保存至:{filename}")
        else:
            print("好的,让我们重新开始。")

if __name__ == "__main__":
    main()