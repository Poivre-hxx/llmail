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
         "content": f"""My game idea is: {user_prompt}
            Please expand this idea into a detailed game design prompt that meets these requirements:
            1. Keep it concise, similar to classic mini-game rules
            2. The prompt will be used to generate Python game code, so keep it focused
            3. Include classic gameplay elements and clear win/lose conditions
            4. Focus on core gameplay mechanics and basic rules"""}
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
         "content": f"""Game design prompt: {game_prompt}
            Create a simple game demo in Python with these requirements:
            1. Screen resolution: 720x480
            2. Use Pygame library
            3. Ensure the game is playable with clear start/end conditions
            4. Use only basic shapes (triangles, circles, squares) for visuals
            5. Include proper game loop, event handling, and collision detection
            6. Add comments explaining key functionality"""}
    ]
    
    if use_claude:
        response = call_claude(messages, temperature=0.2)
    else:
        response = call_ollama(messages, temperature=0.2)
        
    return response if response else "Failed to generate game code."

def check_services():
    """Check if required services are available"""
    services_ok = True
    
    # Check Ollama
    try:
        requests.get("http://localhost:11434")
    except requests.exceptions.ConnectionError:
        print("Warning: Cannot connect to Ollama service")
        services_ok = False
    
    # Check Claude/aisuite configuration
    if not ANTHROPIC_API_KEY:
        print("Warning: ANTHROPIC_API_KEY not found in environment")
        services_ok = False
    
    if not services_ok:
        print("\nPlease ensure:")
        print("1. Ollama is installed and running ('ollama serve')")
        print("2. Required model is installed ('ollama pull qwen2:7b')")
        print("3. ANTHROPIC_API_KEY is set in .env file")
    
    return services_ok

def main():
    print("Welcome to the Game Generator!")
    
    if not check_services():
        return
    
    # Ask user which AI service to use
    use_claude = input("Would you like to use Claude for better quality? (y/n): ").lower() == 'y'
    
    while True:
        user_prompt = input("\nEnter your game idea (or 'q' to quit): ")
        if user_prompt.lower() == 'q':
            print("Thanks for using Game Generator!")
            break
        
        print("\nGenerating detailed game prompt...")
        game_prompt = generate_game_prompt(user_prompt, use_claude)
        print(f"\nGenerated game prompt:\n{game_prompt}")
        
        if input("\nAre you satisfied with this prompt? (y/n): ").lower() == 'y':
            print("\nGenerating Python game code...")
            game_code = generate_game_code(game_prompt, use_claude)
            print(f"\nGenerated game code:\n{game_code}")
            
            filename = f"game_{datetime.now().strftime('%m%d%H%M%S')}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(game_code)
            print(f"\nGame code saved to: {filename}")
        else:
            print("\nOk, let's try again.")

if __name__ == "__main__":
    main()