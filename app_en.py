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
        {"role": "system", "content": "You are a game design assistant. Help expand user's game ideas into detailed game design prompts."},
        {"role": "user", 
        "content": f"""
                    Game Idea: {user_prompt}
                    Expand this idea into a concise and focused game design prompt that follows these guidelines:
                    1. Provide a clear, brief description of the core gameplay and mechanics (similar to classic mini-game rules).
                    2. Ensure the prompt is Python-ready, focusing on the structure of the game (e.g., objects, controls, events).
                    3. Include defined win and lose conditions that are simple and easily understood.
                    4. Highlight classic gameplay elements such as scoring, levels, or challenges, while maintaining simplicity and playability.
                    5. Emphasize basic rules, controls, and interaction that can be translated directly into code.
                    6. You only need to consider basic implementation, without having to consider issues such as sound effects, material textures, etc.
                    """
        }
    ]
    
    response = call_ollama(messages, temperature=0.7)
    return response if response else "游戏prompt生成失败,没有返回结果。"

def generate_game_code(game_prompt):
    """根据详实的游戏prompt,生成对应的Python游戏代码"""
    messages = [
        {"role": "system", "content": "You are a game development engineer who creates Python games based on design prompts."},
        {"role": "user", "content": f"""
                    Game Design Prompt: {game_prompt}
                    Create a simple playable game demo in Python using Pygame with the following requirements:
                    1. Screen resolution: 720x480 pixels.
                    2. Use the Pygame library for all game functionalities.
                    3. The game should be fully playable with clear start and end conditions (win/lose).
                    4. Visuals should be created using basic geometric shapes (e.g., triangles, circles, squares).
                    5. Include a game loop with event handling, and implement basic collision detection.
                    6. Add comments to explain key functions and the game logic.
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
            
            filename = f"game_ollamaen_{datetime.now().strftime('%m%d%H%M%S')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(game_code)
            print(f"游戏代码已保存至:{filename}")
        else:
            print("好的,让我们重新开始。")

if __name__ == "__main__":
    main()