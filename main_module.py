import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import aisuite as ai
from typing import Dict, List, Any
from dataclasses import dataclass

load_dotenv('.env')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = ai.Client()

@dataclass
class GameObjectData:
    id: str
    type: str
    position: tuple
    components: List[str]
    properties: Dict[str, Any]

class ModularGameGenerator:
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.generated_data = {
            "objects": [],
            "systems": [],
            "logic": {},
            "state": {}
        }

    def generate_base_structure(self, user_prompt: str) -> Dict:
        messages = [
            {"role": "system", "content": "You are a game design assistant. Return all responses in valid JSON format."},
            {"role": "user", "content": f"""
Game Idea: {user_prompt}
Generate a basic game structure following:
1. Core gameplay mechanics
2. Basic game objects and their properties
3. Win/lose conditions
4. Basic scoring system
Return ONLY valid JSON with these sections.

Expected format:
{{
    "gameplay": {{
        "mechanics": [],
        "objects": [],
        "win_conditions": [],
        "scoring": {{}}
    }}
}}
"""}
        ]
        response = self.ai_service(messages, temperature=0.7)
        try:
            return json.loads(response) if response else {"gameplay": {}}
        except json.JSONDecodeError:
            print("Error parsing base structure JSON, using default")
            return {"gameplay": {}}

    def generate_game_objects(self, base_structure: Dict) -> List[Dict]:
        messages = [
            {"role": "system", "content": "You are a game objects designer. Return all responses in valid JSON format."},
            {"role": "user", "content": f"""
Based on this game structure:
{json.dumps(base_structure, indent=2)}

Generate game objects with:
1. Object identifiers
2. Type definitions
3. Initial positions
4. Required components
5. Object properties

Return ONLY valid JSON array of objects.

Expected format:
[
    {{
        "id": "player",
        "type": "character",
        "position": [400, 300],
        "components": ["physics", "render", "input"],
        "properties": {{
            "speed": 200
        }}
    }}
]
"""}
        ]
        response = self.ai_service(messages, temperature=0.5)
        try:
            objects_data = json.loads(response) if response else []
            self.generated_data["objects"] = objects_data
            return objects_data
        except json.JSONDecodeError:
            print("Error parsing game objects JSON, using empty list")
            return []

    def generate_components(self, objects_data: List[Dict]) -> str:
        messages = [
            {"role": "system", "content": "You are a game components engineer."},
            {"role": "user", "content": f"""
Based on these game objects:
{json.dumps(objects_data, indent=2)}

Generate complete Python code for components including:
1. Physics components
2. Render components
3. Input handlers
4. Collision components

Return ONLY Python code, no JSON.
"""}
        ]
        response = self.ai_service(messages, temperature=0.3)
        self.generated_data["logic"]["components"] = response or ""
        return response or ""

    def generate_game_systems(self) -> str:
        messages = [
            {"role": "system", "content": "You are a game systems engineer."},
            {"role": "user", "content": f"""
Based on:
Objects: {json.dumps(self.generated_data["objects"], indent=2)}
Components: {json.dumps(self.generated_data["logic"], indent=2)}

Generate complete Python/Pygame implementation including(如果你认为当前的游戏设定下没有必要使用某一个系统，可以选择不生成！):
1. Main game loop
2. Event handling
3. Physics system
4. Collision system
5. State management

Import all required libraries and implement a working game.
"""}
        ]
        response = self.ai_service(messages, temperature=0.3)
        self.generated_data["systems"] = response or ""
        return response or ""

def call_claude(messages, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model="anthropic:claude-3-5-sonnet-20240620",
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip() if response.choices else None
    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None

def call_ollama(messages, model="qwen2:7b", temperature=0.7):
    url = "http://localhost:11434/api/generate"
    prompt = "".join(f"{msg['role']}: {msg['content']}\n" for msg in messages)
    
    try:
        response = requests.post(url, json={
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        })
        response.raise_for_status()
        result = response.json().get("response")
        if not result:
            raise ValueError("Empty response from Ollama")
        return result
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def generate_game(user_prompt: str, use_claude: bool = True) -> str:
    ai_service = call_claude if use_claude else call_ollama
    generator = ModularGameGenerator(ai_service)
    
    print("Step 1: Generating base structure...")
    base_structure = generator.generate_base_structure(user_prompt)
    
    print("Step 2: Generating game objects...")
    game_objects = generator.generate_game_objects(base_structure)
    
    print("Step 3: Generating components...")
    components = generator.generate_components(game_objects)
    
    print("Step 4: Generating game systems...")
    final_code = generator.generate_game_systems()
    
    return final_code

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
    try:
        requests.get("http://localhost:11434")
    except requests.exceptions.ConnectionError:
        print("\nPlease ensure Ollama is running and required model is installed")
    
    if not ANTHROPIC_API_KEY:
        print("\nWarning: ANTHROPIC_API_KEY not found")
    
    return True

def get_user_choice(prompt, options):
    while True:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        try:
            choice = int(input("\nEnter choice number: ").strip())
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print("Invalid choice, try again")

def main():
    print("Welcome to Game Generator!")
    
    if not check_services():
        return
    
    use_claude = input("Use Claude for better quality? (y/n): ").lower() == 'y'
    
    while True:
        user_prompt = input("\nEnter your game idea ('q' to quit): ")
        if user_prompt.lower() == 'q':
            print("Thanks for using Game Generator!")
            break
        
        try:
            game_code = generate_game(user_prompt, use_claude)
            if game_code:
                timestamp = datetime.now().strftime('%m%d%H%M')
                filename = f"module_{timestamp}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(game_code)
                
                print(f"\nGame code saved to: {filename}")
                print("-" * 50)
                print("正在debug")
                debug_code = debug_game_code(game_code, user_prompt, use_claude)
                filename = f"module_debug{datetime.now().strftime('%m%d%H%M')}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(debug_code)
                print(f"\n游戏代码已保存到: {filename}")
            else:
                print("Failed to generate game code. Please try again.")
        except Exception as e:
            print(f"Error during game generation: {e}")
            print("Please try again with a different prompt or check the services.")

if __name__ == "__main__":
    main()