import google.generativeai as genai
from PIL import Image
import random
import os
import time
from termcolor import colored

genai.configure(api_key="keyhere")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

image_folder = r"pathere" # example: C:\\Users\\user\\ImagesReCaptcha
if not os.path.exists(image_folder):
    raise FileNotFoundError(colored(f"The folder {image_folder} does not exist.", 'red'))

flags = {
    "europe": {
        "germany": "germany.png",
        "france": "france.png",
        "italy": "italy.png",
        "spain": "spain.png",
        "uk": "uk.png",
        "portugal": "portugal.png",
        "netherlands": "neitherlands.png",
        "sweden": "sweden.png"
    },
    "south_america": {
        "brazil": "brazil.png",
        "argentina": "argentina.png",
        "chile": "chile.png",
        "colombia": "colombia.png",
        "peru": "peru.png",
        "uruguay": "uruguay.png",
        "paraguay": "paraguay.png"
    },
    "asia": {
        "japan": "japan.png",
        "china": "china.png",
        "south_korea": "sk.png",
        "india": "india.png",
        "thailand": "thailand.png",
        "vietnam": "vietnam.png",
        "malaysia": "malaysia.png",
    }
}

def generate_captcha():
    region = random.choice(list(flags.keys()))
    challenge = f"Select all flags from {region.replace('_', ' ').title()}"
    
    correct_flags = random.sample(list(flags[region].items()), 4)
    incorrect_pool = [item for r in flags if r != region for item in flags[r].items()]
    incorrect_flags = random.sample(incorrect_pool, 5)
    
    all_flags = correct_flags + incorrect_flags
    random.shuffle(all_flags)
    
    grid_size = (600, 600)
    tile_size = (200, 200)
    grid_image = Image.new('RGB', grid_size, 'white')
    
    correct_positions = []
    for idx, (country, filename) in enumerate(all_flags):
        x, y = (idx % 3) * tile_size[0], (idx // 3) * tile_size[1]
        flag_path = os.path.join(image_folder, filename)
        try:
            with Image.open(flag_path) as flag:
                flag = flag.resize(tile_size)
                grid_image.paste(flag, (x, y))
                if (country, filename) in correct_flags:
                    correct_positions.append(idx)
        except Exception as e:
            print(colored(f"Error processing image {flag_path}: {e}", 'red'))
    
    grid_path = os.path.join(image_folder, 'captcha_grid.png')
    grid_image.save(grid_path)
    return [challenge, correct_positions, grid_path]

def solve_captcha(captcha_data):
    try:
        challenge_text = captcha_data[0]
        correct_positions = captcha_data[1]
        img_path = captcha_data[2]
        
        prompt = (
            f"This is a CAPTCHA challenge: {challenge_text}\n"
            "The image shows a 3x3 grid of flags, numbered from 0 to 8, as illustrated below:\n"
            "0 1 2\n"
            "3 4 5\n"
            "6 7 8\n\n"
            "Each number in the grid corresponds to a specific flag. The flags are randomly placed in the grid, and each flag belongs to a particular country or region.\n"
            "Your task is to carefully examine the flags and identify which ones match the given challenge. The challenge will ask you to select flags from a specific region or country.\n\n"
            "For example, if the challenge asks you to select all flags from Europe, and the flags at positions 0, 2, and 6 are the correct European flags, you should respond with '0,2,6'.\n\n"
            "Please remember the following guidelines:\n"
            "1. Each flag in the grid is numbered from 0 to 8.\n"
            "2. You should select only the positions of the flags that match the challenge.\n"
            "3. Do not select any positions that do not match the challenge.\n"
            "4. Your response should only contain the numbers of the selected positions, separated by commas. For example, '0,2,6'.\n"
            "5. Do not include any other text in your response, such as explanations or extra information.\n\n"
            "Your response should be a simple list of numbers, without any punctuation other than commas between the numbers. Please be as accurate as possible."
        )
        
        img = Image.open(img_path)
        response = model.generate_content([prompt, img])
        
        print("AI response:", response.text)
        
        if not response.text.strip():
            raise ValueError("Empty or invalid response from the model.")
        
        selected_positions = [int(pos.strip()) for pos in response.text.split(',')]
        print("selected positions:", selected_positions)
        
        selected = set(selected_positions)
        correct = set(correct_positions)
        
        accuracy = len(selected & correct) / len(correct) * 100 if correct else 0
        
        if accuracy == 0:
            print(f"[!] AI Dont selected. position correct: {sorted(correct_positions)}")
        
        return accuracy
    except Exception as e:
        print(colored(f"error, please report: {e}", 'red'))
        return 0

def run_tests():
    total_tests = 20
    correct_count = 0
    incorrect_count = 0
    
    for i in range(total_tests):
        print(f"\n[!] captcha number {i+1}")
        
        try:
            challenge = generate_captcha()
            print(f"[+] captcha: {challenge[0]}")
            
            accuracy = solve_captcha([challenge[0], challenge[1], challenge[2]])
            
            if accuracy >= 75:
                correct_count += 1
            else:
                incorrect_count += 1
            
            time.sleep(5)
        
        except Exception as e:
            print(f"[!] Error generating CAPTCHA: {e}")
    
    print(f"\n[CaptchaGenie] test completed!")
    print(f"[+] total: {total_tests}")
    print(f"[+] correct: {correct_count}")
    print(f"[+] incorrect: {incorrect_count}")
    print(f"[+] rate: {correct_count / total_tests * 100:.2f}%")

if __name__ == "__main__":
    run_tests()
