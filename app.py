import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shiny.com Analytics - Pokemon Starter", layout="wide")

# ข้อมูลโอกาส (Odds) ตามหน้าเว็บจริง
PACK_ODDS = {
    "SHINY": 0.005,
    "PLATINUM": 0.063,
    "GOLD": 0.432,
    "SILVER": 0.075,
    "BRONZE": 0.425
}

# --- เชื่อมต่อ Google Sheets ผ่าน ID ของคุณ ---
SHEET_ID = "https://script.google.com/macros/s/AKfycbxiXg2E5ejd6Rw-AjHoFtX9du1R6Qls0V-iqHuoiKJ444c-048ZEEuE_iwjffr2blSH/exec"
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def load_data():
    try:
        # ดึงข้อมูลจาก Google Sheets (ต้องตั้งค่าแชร์เป็น 'Anyone with the link' ก่อนนะครับ)
        df = pd.read_csv(sheet_url)
        df['Tier'] = df['Tier'].str.upper()
        return df
    except Exception as e:
        return pd.DataFrame(columns=['Time', 'Tier', 'User', 'Card', 'Stage', 'Value'])

# --- ส่วนแสดงผลหน้าเว็บ ---
st.title("🔥 Pokemon Starter Pack Real-time Monitor (Cloud)")
st.markdown("ระบบวิเคราะห์สถิติจริงจาก Google Sheets")

placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        if not df.empty:
            # 1. แถบตัวเลขสรุป (Metrics)
            total_spins = len(df)
            total_val = df['Value'].sum()
            last_hit = df['Tier'].iloc[-1]
            last_user = df['User'].iloc[-1]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("จำนวนจุ่มทั้งหมด", f"{total_spins} ครั้ง")
            col2.metric("มูลค่าการ์ดรวม", f"${total_val:,.2f}")
            col3.metric("ล่าสุดระดับ", last_hit)
            col4.metric("ผู้เล่นล่าสุด", last_user)

            st.divider()

            # 2. กราฟและการวิเคราะห์
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.subheader("📊 สถิติการออกแต่ละระดับ")
                stats = df['Tier'].value_counts().reset_index()
                stats.columns = ['Tier', 'Real_Count']
                stats['Expected_Count'] = stats['Tier'].map(lambda x: total_spins * PACK_ODDS.get(x, 0))
                
                fig = px.bar(stats, x='Tier', y=['Real_Count', 'Expected_Count'], barmode='group')
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")

            with c2:
                st.subheader("💡 วิเคราะห์ดวง (Hot/Cold)")
                for tier, prob in PACK_ODDS.items():
                    actual = (df['Tier'] == tier).sum()
                    expected = total_spins * prob
                    diff = expected - actual
                    status = "🔥 HOT" if diff > 0 else "❄️ COLD"
                    st.write(f"**{tier}**: {status}")

            # 3. ตารางประวัติล่าสุด
            st.subheader("📋 รายการจุ่มล่าสุด")
            st.dataframe(df.tail(10).iloc[::-1], use_container_width=True)
            
        else:
            st.info("⌛ กำลังรอข้อมูลไหลเข้า Google Sheets... กรุณารันบอทในคอมทิ้งไว้")

    time.sleep(15) # อัปเดตทุก 15 วินาที (เพื่อไม่ให้ Google แบนการเข้าถึงบ่อยเกินไป)
