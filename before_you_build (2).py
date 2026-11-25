import streamlit as st, json, math
from urllib.parse import quote_plus
from pathlib import Path
from datetime import date
st.set_page_config(page_title="Before You Build",page_icon="⚙️",layout="wide")
st.markdown("""<style>
.stApp{background:#07111f;color:#f8fafc}h1,h2,h3{color:#67e8f9!important}
p,label,li,[data-testid=stWidgetLabel]{color:#f1f5f9!important}
input,textarea,[data-baseweb=select]>div{background:#f8fafc!important;color:#111827!important}
input,textarea{-webkit-text-fill-color:#111827!important} [data-baseweb=select] *{color:#111827!important}
.stButton button,.stDownloadButton button{background:#087fae;color:white;border:1px solid #67e8f9;font-weight:700}
[data-testid=stMetric]{background:#142943;border:1px solid #5b7d9e;padding:12px;border-radius:10px}
[data-testid=stMetricLabel],[data-testid=stMetricValue]{color:white!important}
section[data-testid=stSidebar]{background:#101f33}
</style>""",unsafe_allow_html=True)
# Component database: item -> (estimated INR, work-hours)
C={"Arduino Uno":(450,2),"Arduino Nano":(300,2),"ESP32":(400,2),"Raspberry Pi Pico":(500,2),"Ultrasonic Sensor":(120,1),"IR Sensor":(80,1),"PIR Motion Sensor":(130,1),"Line Tracking Sensor":(150,1),"DHT11 Sensor":(100,1),"DHT22 Sensor":(220,1),"Soil Moisture Sensor":(100,1),"Rain Sensor":(90,1),"Gas Sensor MQ-2":(160,1),"Flame Sensor":(100,1),"Water Level Sensor":(90,1),"RFID Reader":(180,1),"RFID Card":(25,.2),"LDR Sensor":(40,.5),"Sound Sensor":(80,1),"Bluetooth HC-05":(350,1),"Wi-Fi Module":(180,1),"GPS Module":(650,2),"Servo Motor":(180,2),"DC Gear Motor":(160,2),"Motor Driver L298N":(180,1),"Relay Module":(100,1),"Buzzer":(30,.2),"LED":(10,.2),"RGB LED":(35,.3),"LCD 16x2":(200,1),"OLED Display":(250,1),"Breadboard":(100,.5),"Jumper Wires":(60,.5),"Battery Pack":(180,1),"Solar Panel":(450,1),"Push Button":(10,.2),"Water Pump":(250,1),"Micro SD Module":(100,1),"Camera Module":(900,2),
# --- newly added components ---
"Arduino Mega":(1100,2),"ESP8266 NodeMCU":(350,2),"STM32 Blue Pill":(450,2),"Raspberry Pi 4":(5500,3),"ESP32-CAM":(900,2),"Joystick Module":(90,.5),"Potentiometer":(30,.3),"Touch Sensor TTP223":(40,.5),"Hall Effect Sensor":(60,.5),"Vibration Sensor":(70,.5),"Pressure Sensor BMP180":(250,1),"MPU6050 Gyro/Accelerometer":(280,1.5),"Current Sensor ACS712":(200,1),"Voltage Sensor":(80,.5),"Load Cell HX711":(300,1.5),"Color Sensor TCS3200":(400,1.5),"Fingerprint Sensor":(1800,2),"Temperature Sensor DS18B20":(90,1),"Pulse Heart Rate Sensor":(150,1),"Keypad 4x4":(90,1),"7-Segment Display":(50,.5),"TFT Display":(550,1.5),"Stepper Motor NEMA17":(900,2),"28BYJ-48 Stepper Motor":(180,1),"Stepper Driver A4988":(150,1),"BLDC Motor":(600,2),"MG995 Servo":(450,2),"Solenoid Valve":(350,1),"LoRa Module":(700,2),"NRF24L01 Module":(180,1),"GSM Module SIM800L":(600,2),"RTC DS3231":(150,1),"Level Shifter":(40,.3),"Buck Converter":(60,.5),"Li-ion 18650 Cell":(120,.5),"TP4056 Charger":(40,.5),"Speaker":(60,.5),"Transistor":(5,.2),"Resistor Pack":(50,.3),"Capacitor Pack":(50,.3),"Robot Chassis Kit":(450,2),"Wheels (pair)":(80,.5)}
# Built-in project: category, problem, components, suggested budget
P={
"Obstacle Detection Robot":("Robotics","A mobile robot that detects nearby obstacles and changes direction.","Arduino Uno,Ultrasonic Sensor,Servo Motor,DC Gear Motor,Motor Driver L298N,Battery Pack,Jumper Wires",2500),
"Line Following Robot":("Robotics","A robot that follows a marked path using infrared sensors.","Arduino Nano,Line Tracking Sensor,DC Gear Motor,Motor Driver L298N,Battery Pack",2200),
"Smart Dustbin":("Automation","A touch-free bin that opens its lid when someone approaches.","Arduino Uno,Ultrasonic Sensor,Servo Motor,Buzzer,Battery Pack",1300),
"Home Automation":("IoT","A phone-controlled model for switching household devices.","ESP32,Relay Module,Bluetooth HC-05,LED,Breadboard,Jumper Wires",1600),
"Weather Monitoring Station":("IoT","A device that measures and displays local temperature and humidity.","ESP32,DHT22 Sensor,LCD 16x2,Wi-Fi Module,Breadboard",1300),
"Smart Irrigation System":("Smart Systems","A soil-moisture based model that controls a small water pump.","Arduino Uno,Soil Moisture Sensor,Relay Module,Water Pump,LCD 16x2",1500),
"Gas Leakage Alert":("Smart Systems","A model that detects gas and gives an audible warning.","Arduino Uno,Gas Sensor MQ-2,Buzzer,LED,LCD 16x2",900),
"Smart Parking System":("Automation","A model that detects vehicle presence and displays parking status.","Arduino Uno,Ultrasonic Sensor,IR Sensor,LCD 16x2,LED,Buzzer",1100),
"RFID Attendance System":("Automation","A prototype that reads RFID cards and displays attendance status.","Arduino Uno,RFID Reader,RFID Card,LCD 16x2,Buzzer",1100),
"Water Level Indicator":("Smart Systems","A system that indicates the level of water in a tank.","Arduino Uno,Water Level Sensor,LED,Buzzer,LCD 16x2",800),
"Plant Health Monitor":("IoT","A monitor that tracks soil moisture and surrounding conditions.","ESP32,Soil Moisture Sensor,DHT11 Sensor,OLED Display,Wi-Fi Module",1200),
"Automatic Street Light":("Automation","A light model that switches on when ambient light is low.","Arduino Nano,LDR Sensor,LED,Relay Module,Breadboard",550),
"Solar Tracking Model":("Robotics","A model that adjusts a panel toward brighter light.","Arduino Uno,LDR Sensor,Servo Motor,Solar Panel,Battery Pack",1400),
"Bluetooth Controlled Car":("Robotics","A small car controlled wirelessly from a phone.","Arduino Uno,Bluetooth HC-05,DC Gear Motor,Motor Driver L298N,Battery Pack",2200),
"Fire Alert Prototype":("Smart Systems","A sensor-based model that gives an alert when flame is detected.","Arduino Uno,Flame Sensor,Buzzer,LED,LCD 16x2",850)}
BASE={"Robotics":5,"IoT":4,"Automation":4,"Smart Systems":3,"Other":3}; MULT={"Beginner":1,"Intermediate":1.5,"Advanced":2}
DEF={"project":"Custom project","name":"","purpose":"","category":"Robotics","budget":2000,"level":"Beginner","team":1,"hours":4,"parts":[],"qty":{},"custom":{}}
for k,v in DEF.items(): st.session_state.setdefault(k,v); st.session_state[k]=st.session_state[k]  # keeps values alive on pages where the widget isn't shown (fixes empty report)
A={**C,**st.session_state.custom}  # built-in + user-added components
def load_preset():
    n=st.session_state.project
    if n in P:
        cat,purpose,parts,budget=P[n]; st.session_state.update(name=n,purpose=purpose,category=cat,budget=budget,parts=parts.split(","),qty={x:1 for x in parts.split(",")})
def add_custom():
    n=st.session_state.cn.strip()
    if n: st.session_state.custom[n]=(st.session_state.cp,st.session_state.ch); st.session_state.parts=list(dict.fromkeys([*st.session_state.parts,n])); st.session_state.qty.setdefault(n,1)
st.title("⚙️ BEFORE YOU BUILD")
st.caption("Think. Simulate. Build. | Plan your engineering project before you start building.")
page=st.sidebar.radio("NAVIGATION",["Dashboard","Idea Lab","Component Lab","Cost & Time","Procurement","Feasibility","Roadmap","Report"])
st.sidebar.selectbox("START WITH A BUILT-IN PROJECT",["Custom project",*P],key="project",on_change=load_preset)
if page=="Idea Lab":
    st.header("💡 IDEA LAB"); st.text_input("Project name",key="name",placeholder="Write your project name..."); st.text_area("Project topic / problem",key="purpose",placeholder="Describe what your project solves...")
    st.selectbox("Category",list(BASE),key="category"); st.number_input("Estimated budget (₹)",100,100000,key="budget",step=100); st.selectbox("Difficulty",list(MULT),key="level"); st.number_input("Team members",1,20,key="team"); st.number_input("Hours per person per day",1,12,key="hours")
    if st.button("SAVE PROJECT DETAILS"): st.success("Project details saved for this session.")
elif page=="Component Lab":
    st.header("🔧 COMPONENT LAB"); q=st.text_input("🔍 Search components",placeholder="Type e.g. sensor, motor, display...").strip().lower()
    opts=[x for x in A if q in x.lower() or x in st.session_state.parts]; st.caption(f"{sum(q in x.lower() for x in A)} of {len(A)} components match")
    st.multiselect("Select components",opts,key="parts")
    with st.expander("➕ Add your own component"):
        st.text_input("Component name",key="cn"); st.number_input("Price each (₹)",1,100000,100,key="cp"); st.number_input("Work-hours needed",0.0,50.0,1.0,step=0.5,key="ch"); st.button("ADD COMPONENT",on_click=add_custom)
    for x in st.session_state.parts: st.session_state.qty[x]=st.number_input(f"{x} — ₹{A[x][0]} each",1,100,int(st.session_state.qty.get(x,1)),key="qty_"+x)
    st.metric("Estimated component cost",f"₹{sum(A[x][0]*st.session_state.qty.get(x,1) for x in st.session_state.parts):,}")
else:
    parts=st.session_state.parts; cost=sum(A[x][0]*st.session_state.qty.get(x,1) for x in parts); work=sum(A[x][1]*st.session_state.qty.get(x,1) for x in parts); hours=math.ceil((BASE[st.session_state.category]+work)*MULT[st.session_state.level]); days=math.ceil(hours/(st.session_state.team*st.session_state.hours)); left=st.session_state.budget-cost
    if page=="Dashboard":
        st.header("PROJECT DASHBOARD"); st.info("Choose a built-in project in the sidebar or create your own in Idea Lab."); st.subheader(st.session_state.name or "Your project will appear here"); st.write(st.session_state.purpose); a,b,c=st.columns(3); a.metric("Category",st.session_state.category); b.metric("Budget",f"₹{st.session_state.budget:,}"); c.metric("Components",len(parts)); st.write("**Selected:** "+(", ".join(parts) if parts else "None yet"))
    elif page=="Cost & Time":
        st.header("📊 COST & TIME"); a,b,c=st.columns(3); a.metric("Estimated cost",f"₹{cost:,}"); b.metric("Budget",f"₹{st.session_state.budget:,}"); c.metric("Remaining",f"₹{left:,}"); a,b=st.columns(2); a.metric("Estimated work",f"{hours} hours"); b.metric("Estimated completion",f"{days} days")
    elif page=="Procurement":
        st.header("🛒 PROCUREMENT")
        for x in parts:
            st.write(f"**{x}** — ₹{A[x][0]} × {st.session_state.qty.get(x,1)}"); q=quote_plus(x); a,b=st.columns(2); a.link_button("Search Amazon",f"https://www.amazon.in/s?k={q}"); b.link_button("Search Flipkart",f"https://www.flipkart.com/search?q={q}")
    elif page=="Feasibility":
        st.header("📊 FEASIBILITY & RISK"); (st.success if left>=0 else st.error)("Within budget" if left>=0 else "Estimated cost exceeds budget"); st.write(f"Technical: check component compatibility and controller capacity.\n\nBudget: ₹{cost:,} estimated against ₹{st.session_state.budget:,}.\n\nTime: approximately {days} days.\n\nTeam: {st.session_state.team} member(s).\n\nSafety: follow instructor and laboratory guidance.")
        for x in parts:
            if x in ["DC Gear Motor","Servo Motor","Water Pump","MG995 Servo","BLDC Motor","Stepper Motor NEMA17"]: st.warning(f"{x}: check motor/pump voltage and current requirements.")
            if x in ["Arduino Uno","Arduino Nano","Arduino Mega","ESP32","ESP8266 NodeMCU","STM32 Blue Pill"]: st.warning(f"{x}: check controller pins, voltage levels and memory limits.")
    elif page=="Roadmap":
        st.header("📅 PROJECT ROADMAP");
        for i,s in enumerate(["Research and identify the problem","Plan the design","Procure components","Assemble prototype","Program and integrate","Test and debug","Improve and document"],1): st.write(f"**Stage {i}:** {s}")
        st.success(f"Estimated completion: {days} days")
    elif page=="Report":
        st.header("📄 PROJECT REPORT"); S=st.session_state; report=f"BEFORE YOU BUILD\nProject Name: {S.name or 'Not entered'}\nProject Topic: {S.purpose or 'Not entered'}\nCategory: {S.category}\nDifficulty: {S.level}\nTeam: {S.team} member(s)\nComponents: {', '.join(f'{x} x{S.qty.get(x,1)}' for x in parts) or 'None'}\nCost: ₹{cost}\nBudget: ₹{S.budget}\nRemaining: ₹{left}\nEstimated time: {days} days\nGenerated: {date.today()}"; st.text(report); st.download_button("DOWNLOAD REPORT",report,"before_you_build_report.txt")
    if page!="Dashboard": st.caption("All prices and time values are illustrative estimates. Verify specifications and prices before purchasing.")
st.sidebar.caption("BEFORE YOU BUILD • Engineering project planner")
