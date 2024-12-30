import google.generativeai as genai
from PIL import Image
import time
import random
import string
import os
from captcha.image import ImageCaptcha

genai.configure(api_key="keyhere")
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def log(msg, color='green', to_file=False):
    colors = {'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m', 'reset': '\033[0m'}
    print(f"{colors.get(color, colors['reset'])}{msg}{colors['reset']}")
    
    if to_file:
        with open('log.txt', 'a') as log_file:
            log_file.write(msg + '\n')

def random_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_captcha(text):
    if not os.path.exists('captchas'):
        os.makedirs('captchas')
    img = ImageCaptcha(width=280, height=90)
    path = f"captchas/{text}.png"
    img.write(text, path)
    return path, text

def solve_captcha(text, img_path):
    try:
        img = Image.open(img_path)
        input_data = [text, img]
        response = model.generate_content(f"Solve the challenge: {input_data}")
        return response.text.strip()
    except Exception as e:
        log(f"[!] Error: {e}", 'red', to_file=True)
        return None

def run_test(success_count, failure_count):
    text = random_text()
    img_path, original = create_captcha(text)
    log(f"[+] testing CAPTCHA: {text}", 'yellow', to_file=True)
    result = solve_captcha(text, img_path)
    
    if result:
        if result == text:
            log(f"[+] Correct: {result}", 'green', to_file=True)
            success_count += 1
        else:
            log(f"[!] incorrect: {result} (Expected: {text})", 'red', to_file=True)
            failure_count += 1
    else:
        log(f"[!] failed to solve.", 'red', to_file=True)
        failure_count += 1
    
    log(f"[-] saved: {img_path}", 'yellow', to_file=True)
    time.sleep(5)
    
    return success_count, failure_count

def main():
    success_count = 0
    failure_count = 0
    total_tests = 20
    
    if os.path.exists('log.txt'):
        os.remove('log.txt')
    
    while success_count + failure_count < total_tests:
        success_count, failure_count = run_test(success_count, failure_count)
    
    success_rate = (success_count / total_tests) * 100
    log(f"\ntest: {total_tests}", 'yellow', to_file=True)
    log(f"correct: {success_count}", 'green', to_file=True)
    log(f"incorrect: {failure_count}", 'red', to_file=True)
    log(f"rate %: {success_rate:.2f}%", 'green', to_file=True)

main()
