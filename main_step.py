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

class GameGenerator:
    def __init__(self, ai_service, user_prompt: str):
        self.ai_service = ai_service
        self.user_prompt = user_prompt
        self.game_type = None
        self.template = None

    def analyze_game_type(self) -> str:
        messages = [
            {"role": "system", "content": "You are a game design expert."},
            {"role": "user", "content": f"""
Analyze this game idea and classify it: {self.user_prompt}

Return ONLY valid JSON:
{{
    "game_type": "platform"|"puzzle"|"shooter"|"arcade",
    "core_mechanics": ["mechanic1", "mechanic2"],
    "key_features": ["feature1", "feature2"]
}}
"""}
        ]
        response = self._parse_json_response(self.ai_service(messages))
        self.game_type = response.get("game_type")
        return response

    def load_game_template(self) -> Dict:
        messages = [
            {"role": "system", "content": "You are a game template specialist. Generate a complete and structured template."},
            {"role": "user", "content": f"""
Generate base template for {self.game_type} game with:
{self.user_prompt}

Required classes:
1. Game (main class)
2. Player
3. Level/World
4. Objects/Entities
5. UI/HUD

Template must include imports and class structure.
"""}
        ]
        self.template = self.ai_service(messages)
        return self.template

    def generate_complete_game(self) -> str:
        messages = [
            {"role": "system", "content": "You are a Pygame expert. Generate complete, working game code."},
            {"role": "user", "content": f"""
Create a complete Pygame game:
Game Type: {self.game_type}
User Idea: {self.user_prompt}
Base Template: {self.template}

Requirements:
1. Screen size: 800x600, 60 FPS
2. Complete game states (menu, play, pause, game over)
3. Basic shapes for visuals (pygame.draw)
4. Collision detection
5. Score/lives system
6. Clean code structure with comments

Return complete, runnable Python code using Pygame.
"""}
        ]
        return self.ai_service(messages) or ""

    def optimize_and_debug(self, game_code: str) -> str:
        messages = [
            {"role": "system", "content": "You are a Python game optimization expert."},
            {"role": "user", "content": f"""
Debug and optimize this {self.game_type} game:
{game_code}

Focus on:
1. Fix any bugs or issues
2. Optimize performance
3. Improve game balance
4. Add error handling
5. Clean up code structure

Return complete, improved game code.
"""}
        ]
        return self.ai_service(messages) or game_code

    def _parse_json_response(self, response: str) -> Dict:
        try:
            return json.loads(response) if response else {}
        except json.JSONDecodeError:
            print("JSON parsing error")
            return {}

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
        return response.json().get("response")
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def generate_game(user_prompt: str, use_claude: bool = True) -> str:
    ai_service = call_claude if use_claude else call_ollama
    generator = GameGenerator(ai_service, user_prompt)
    
    print("Analyzing game type...")
    game_info = generator.analyze_game_type()
    print(f"Detected game type: {generator.game_type}")
    
    print("Loading game template...")
    generator.load_game_template()
    
    print("Generating complete game...")
    game_code = generator.generate_complete_game()
    
    print("Optimizing and debugging...")
    final_code = generator.optimize_and_debug(game_code)
    
    return final_code

def check_services():
    try:
        requests.get("http://localhost:11434")
    except requests.exceptions.ConnectionError:
        print("\nPlease ensure Ollama is running")
    if not ANTHROPIC_API_KEY:
        print("\nWarning: ANTHROPIC_API_KEY not found")
    return True

def main():
    print("Game Generator 3.0")
    if not check_services():
        return
    
    use_claude = input("Use Claude for better quality? (y/n): ").lower() == 'y'
    
    while True:
        user_prompt = input("\nEnter game idea ('q' to quit): ")
        if user_prompt.lower() == 'q':
            break
        
        try:
            game_code = generate_game(user_prompt, use_claude)
            if game_code:
                timestamp = datetime.now().strftime('%m%d%H%M')
                filename = f"game_{timestamp}.py"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(game_code)
                print(f"\nGame saved to: {filename}")
                print("\nOptimizing code...")
                optimized_code = GameGenerator(
                    call_claude if use_claude else call_ollama,
                    user_prompt
                ).optimize_and_debug(game_code)
                debug_filename = f"game_optimized_{timestamp}.py"
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(optimized_code)
                print(f"Optimized code saved to: {debug_filename}")
            else:
                print("Generation failed. Please try again.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()