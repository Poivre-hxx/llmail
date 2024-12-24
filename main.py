import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import aisuite as ai

# Load environment variables
load_dotenv('.env')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Initialize aisuite client
client = ai.Client()

def call_claude(messages, temperature=0.7):
    """Call Claude using aisuite"""
    try:
        response = client.chat.completions.create(
            model="anthropic:claude-3-5-sonnet-20240620",
            messages=messages,
            temperature=temperature
        )
        
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            print("Warning: No content found in response")
            return None
            
    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None

def call_ollama(messages, model="qwen2:7b", temperature=0.7):
    """Call local Ollama service"""
    url = "http://localhost:11434/api/generate"
    
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"System: {msg['content']}\n"
        else:
            prompt += f"{msg['content']}\n"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "response" in result:
            return result["response"]
        else:
            print("Warning: No 'response' field found")
            return None
            
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def generate_game_prompt(user_prompt, use_claude=True):
    """Generate detailed game prompt from user idea"""
    messages = [
        {"role": "system", "content": "You are a game design assistant. Help expand user's game ideas into detailed game design prompts."},
        {"role": "user", 
         "content": f"""Game Idea: {user_prompt}
            Expand this idea into a concise and focused game design prompt that follows these guidelines:
            1. Provide a clear, brief description of the core gameplay and mechanics (similar to classic mini-game rules).
            2. Ensure the prompt is Python-ready, focusing on the structure of the game (e.g., objects, controls, events).
            3. Include defined win and lose conditions that are simple and easily understood.
            4. Highlight classic gameplay elements such as scoring, levels, or challenges, while maintaining simplicity and playability.
            5. Emphasize basic rules, controls, and interaction that can be translated directly into code.
            6. You only need to consider basic implementation, without having to consider issues such as sound effects, material textures, etc.
            7. Considering the limitation of the length of the token, the more streamlined the better, keeping only the necessary features.
            """
        }
    ]
    
    if use_claude:
        response = call_claude(messages, temperature=0.7)
    else:
        response = call_ollama(messages, temperature=0.7)
        
    return response if response else "Failed to generate game prompt."

def generate_game_code(game_prompt, use_claude=True):
    """Generate Python game code from the detailed prompt"""
    messages = [
        {"role": "system", "content": "You are a game development engineer who creates Python games based on design prompts."},
        {"role": "user", 
         "content": f"""Game Design Prompt: {game_prompt}
                Create a simple playable game demo in Python using Pygame with the following requirements:
                1. Screen resolution: 720x480 pixels.
                2. Use the Pygame library for all game functionalities.
                3. The game should be fully playable with clear start and end conditions (win/lose).
                4. Visuals should be created using basic geometric shapes (e.g., triangles, circles, squares).
                5. Include a game loop with event handling, and implement basic collision detection.
                6. Consider the libraries you use and make sure they are complete
                """
        }
    ]
    
    if use_claude:
        response = call_claude(messages, temperature=0.2)
    else:
        response = call_ollama(messages, temperature=0.2)
        
    return response if response else "Failed to generate game code."

def debug_game_code(game_code, game_prompt, use_claude=True):
    """Debug Python game code from the detailed prompt"""
    messages = [
        {"role": "system", "content": "You are a QA engineer who debugs Python games."},
        {"role": "user", 
         "content": f"""Game Design Prompt: {game_prompt}
                        Game Code: {game_code}
                你需要对照Game Design Prompt以及游戏的可玩性对目前的Game Code进行debug，并且输出改进后的整个游戏代码。
                务必注意以下几点：
                1. 确保游戏的可玩性.
                2. 游戏需要对照并实现design prompt的需求。
                """
        }
    ]
    
    if use_claude:
        response = call_claude(messages, temperature=0.2)
    else:
        response = call_ollama(messages, temperature=0.2)
        
    return response if response else "Failed to generate game code."

def check_services():
    """Check if required services are available"""
    
    # Check Ollama
    try:
        requests.get("http://localhost:11434")
    except requests.exceptions.ConnectionError:
        print("\nPlease ensure:")
        print("1. Ollama is installed and running ('ollama serve')")
        print("2. Required model is installed ('ollama pull qwen2:7b')")
    
    # Check Claude/aisuite configuration
    if not ANTHROPIC_API_KEY:
        print("\nPlease ensure:")
        print("Warning: ANTHROPIC_API_KEY not found in environment")
    
    return True

def get_user_choice(prompt, options):
    """获取用户选择"""
    import sys
    import time
    
    def flush_input():
        """清空输入缓冲区"""
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys, termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    
    # 清空输入缓冲区
    flush_input()
    
    while True:
        # 打印选项
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
            
        # 确保输出完全显示
        sys.stdout.flush()
        time.sleep(0.1)
        
        # 获取用户输入
        try:
            choice = input("\n请选择 (输入数字): ").strip()
            if not choice:  # 如果是空输入，继续循环
                continue
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print("无效的选择，请重试")

def main():
    print("欢迎使用游戏生成器！")
    
    if not check_services():
        return
    
    # Ask user which AI service to use
    use_claude = input("是否使用Claude来获得更好的生成质量? (y/n): ").lower() == 'y'
    
    while True:
        user_prompt = input("\n请输入你的游戏创意 (输入 'q' 退出): ")
        if user_prompt.lower() == 'q':
            print("感谢使用游戏生成器！")
            break
        
        while True:
            print("\n正在生成详细的游戏设计方案...")
            game_prompt = generate_game_prompt(user_prompt, use_claude)
            print("\n生成的游戏设计方案:")
            print("-" * 50)
            print(game_prompt)
            print("-" * 50)
            
            # 让用户选择下一步操作
            options = ["继续生成游戏代码", "重新生成设计方案", "输入新的游戏创意"]
            choice = get_user_choice("对生成的设计方案满意吗？请选择:", options)
            
            if choice == 1:  # 继续生成代码
                print("\n正在生成Python游戏代码...")
                game_code = generate_game_code(game_prompt, use_claude)
                filename = f"game_{datetime.now().strftime('%m%d%H%M')}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(game_code)
                print(f"\n游戏代码已保存到: {filename}")
                print("\n生成的游戏代码:")
                print("-" * 50)
                print(game_code)
                print("-" * 50)
                debug_code = debug_game_code(game_code, game_prompt, use_claude)
                filename = f"game_debug{datetime.now().strftime('%m%d%H%M')}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(debug_code)
                print(f"\n游戏代码已保存到: {filename}")
                break
            elif choice == 2:  # 重新生成设计方案
                continue
            else:  # 输入新的创意
                break

if __name__ == "__main__":
    main()