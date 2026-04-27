import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- ข้อมูลราคาประเมิน (อ้างอิงจากหน้าเว็บ) ---
VALUES = {"SHINY": 300, "PLATINUM": 56, "GOLD": 31, "SILVER": 22, "BRONZE": 15}
FILE_NAME = "shiny_history.csv"

def save_to_file(tier, user, card_name, stage):
    val = VALUES.get(tier.upper(), 0)
    df = pd.DataFrame([[time.strftime("%Y-%m-%d %H:%M:%S"), tier, user, card_name, stage, val]], 
                      columns=['Time', 'Tier', 'User', 'Card', 'Stage', 'Value'])
    if not os.path.isfile(FILE_NAME):
        df.to_csv(FILE_NAME, index=False)
    else:
        df.to_csv(FILE_NAME, mode='a', header=False, index=False)
    print(f"✅ บันทึก [ {tier} ] | User: {user} | Stage: {stage}")

def run_realtime_ai():
    print("🤖 กำลังเริ่มหุ่นยนต์สแกนเนอร์: เป้าหมาย Pokemon Starter Pack")
    
    # ตั้งค่าให้ Chrome เปิดมาแบบเสถียร
    chrome_options = Options()
    # chrome_options.add_argument("--start-maximized") # เปิดแบบเต็มจอ
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # --- แก้ไข Link ให้เจาะจงหน้านี้โดยเฉพาะ ---
    target_url = "https://shiny.com/packs/PokemonStarterPack"
    driver.get(target_url)
    
    print("📢 กรุณารอ 10 วินาทีให้หน้าเว็บและ Live Hits โหลด...")
    time.sleep(10)

    processed_cards = [] 

    while True:
        try:
            # 1. ดึงข้อมูล Stage ปัจจุบัน
            stage_el = driver.find_element(By.CLASS_NAME, "jp2-stage-label")
            current_stage = stage_el.text.strip() if stage_el else "N/A"

            # 2. ดึงรายการ Live Hits ทั้งหมดจากโครงสร้างที่คุณหามา
            hit_items = driver.find_elements(By.CLASS_NAME, "live-hit-item")
            
            for item in hit_items:
                # ดึงชื่อการ์ด (ใช้เป็น ID กันบันทึกซ้ำ)
                img_el = item.find_element(By.TAG_NAME, "img")
                card_name = img_el.get_attribute("alt")
                
                if card_name not in processed_cards:
                    # ดึงระดับ (Tier) และชื่อผู้เล่น (User)
                    tier = item.find_element(By.CLASS_NAME, "font-bold").text
                    user = item.find_element(By.CLASS_NAME, "live-hit-user").text
                    
                    save_to_file(tier, user, card_name, current_stage)
                    processed_cards.append(card_name)
                    
                    # เก็บประวัติในแรม 50 รายการกันบันทึกซ้ำ
                    if len(processed_cards) > 50: processed_cards.pop(0)
                    
        except Exception as e:
            # กรณีหน้าเว็บมีการอัปเดตหรือโหลดไม่ทัน ให้ข้ามไปก่อน
            pass
        
        time.sleep(3) # เช็คทุก 3 วินาที

if __name__ == "__main__":
    run_realtime_ai()
