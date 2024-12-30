import google.generativeai as genai
from PIL import Image
import time
import random
import string
import os
import re
import io
from captcha.image import ImageCaptcha

genai.configure(api_key="keyhere")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def print_log(message, color='green'):
    color_codes = {'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m', 'reset': '\033[0m'}
    print(f"{color_codes.get(color, color_codes['reset'])}{message}{color_codes['reset']}")

def generate_random_text(length=8):
    characters = string.ascii_uppercase + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

def clean_filename(text):
    return re.sub(r'[<>:"/\\|?*]', '_', text)

def create_captcha_image(text):
    if not os.path.exists('captchas'):
        os.makedirs('captchas')
    
    cleaned_text = clean_filename(text)
    img = ImageCaptcha(width=280, height=90)
    path = f"captchas/{cleaned_text}.png"
    img.write(text, path)
    return path, text

def solve_captcha_image(text, img_path):
    try:
        img = Image.open(img_path)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        input_data = [text, img_byte_arr]
        
        response = model.generate_content(
            f"Solve the challenge, for solve this challenge u need get what is at the image writed, "
            f"and return to a writed thing from the image, dont make any explication: {input_data}"
        )
        return response.text.strip()
    except Exception as e:
        print_log(f"[!] Failed: {e}", 'red')
        return None

def calculate_accuracy(expected, predicted):
    correct_chars = sum(1 for e, p in zip(expected, predicted) if e == p)
    accuracy = (correct_chars / len(expected)) * 100
    return accuracy

def run_test():
    text = generate_random_text()
    img_path, original = create_captcha_image(text)
    print_log(f"[+] testing captcha: {text}", 'yellow')
    result = solve_captcha_image(text, img_path)
    
    if result:
        accuracy = calculate_accuracy(text, result)
        if result == text:
            print_log(f"[+] correct: {result} (100% accurate)", 'green')
            return True
        else:
            print_log(f"[!] incorrect: {result} (Expected: {text}) - Accuracy: {accuracy:.2f}%", 'red')
            print_log(f"[!] error: Gemini AI was off by {len(text) - accuracy} characters", 'red')
            return False
    else:
        print_log(f"[!] failed to solve.", 'red')
        return False
    
    print_log(f"[-] Saved: {img_path}", 'yellow')
    time.sleep(3)

def log_results(success_count, total_tests):
    success_rate = (success_count / total_tests) * 100
    with open('logscaptcha.txt', 'w') as log_file:
        log_file.write(f"tests: {total_tests}\n")
        log_file.write(f"sucess rates: {success_count}\n")
        log_file.write(f"rate %: {success_rate:.2f}%\n")
    print_log(f"[+] CAPTCHA Test Results saved to logscaptcha.txt", 'green')

def main():
    success_count = 0
    total_tests = 20
    
    for _ in range(total_tests):
        if run_test():
            success_count += 1
        print_log("[+] cd: wait 5", 'yellow')
        time.sleep(5)
    
    log_results(success_count, total_tests)

main()
