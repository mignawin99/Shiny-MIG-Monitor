import streamlit as st
import pandas as pd
import plotly.express as px
import time

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Shiny.com Analytics - Pokemon Starter", layout="wide")

# ข้อมูลโอกาส (Odds) ตามหน้าเว็บจริง
PACK_ODDS = {
    "SHINY": 0.005,
    "PLATINUM": 0.063,
    "GOLD": 0.432,
    "SILVER": 0.075,
    "BRONZE": 0.425
}

def load_data():
    try:
        df = pd.read_csv("shiny_history.csv")
        df['Tier'] = df['Tier'].str.upper()
        return df
    except:
        return pd.DataFrame(columns=['Time', 'Tier', 'User', 'Card', 'Stage', 'Value'])

# หัวข้อหน้าเว็บ
st.title("🔥 Pokemon Starter Pack Real-time Monitor")
st.markdown("ระบบวิเคราะห์โอกาสการเปิดได้ฮิต และสถิติจาก Live Hits")

# ส่วนอัปเดตข้อมูลอัตโนมัติ
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

            # 2. กราฟวิเคราะห์
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.subheader("📊 สถิติการออกแต่ละระดับ (Real vs Expected)")
                stats = df['Tier'].value_counts().reset_index()
                stats.columns = ['Tier', 'Real_Count']
                
                # คำนวณค่าที่ควรจะเป็น (Expected)
                stats['Expected_Count'] = stats['Tier'].map(lambda x: total_spins * PACK_ODDS.get(x, 0))
                
                fig = px.bar(stats, x='Tier', y=['Real_Count', 'Expected_Count'], 
                             barmode='group', color_discrete_sequence=['#FF4B4B', '#FFAA00'])
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.subheader("💡 วิเคราะห์ดวง (Hot/Cold)")
                for tier, prob in PACK_ODDS.items():
                    actual = (df['Tier'] == tier).sum()
                    expected = total_spins * prob
                    diff = expected - actual
                    
                    if diff > 0:
                        st.success(f"**{tier}**: 🔥 HOT (ขาดช่วงนานแล้ว)")
                    else:
                        st.warning(f"**{tier}**: ❄️ COLD (เพิ่งออกเยอะ)")

            # 3. ตารางประวัติล่าสุด
            st.subheader("📋 10 รายการจุ่มล่าสุด")
            st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)
            
        else:
            st.info("กำลังรอข้อมูลจากหุ่นยนต์... กรุณารัน shiny_realtime.py ทิ้งไว้")

    time.sleep(5) # รีเฟรชทุก 5 วินาที
