# Weather & Air Quality Dashboard 🌦️🍃

### โครงการวิชา Script Programming (CP352301 Sec.1)

เว็บแอปพลิเคชัน Flask ที่รวมข้อมูลสภาพอากาศแบบเรียลไทม์ ดัชนีคุณภาพอากาศ พยากรณ์ล่วงหน้า และคำแนะนำด้านสุขภาพที่สร้างโดยปัญญาประดิษฐ์ไว้ในแดชบอร์ดเดียว ผู้ใช้สามารถค้นหาเมืองที่ต้องการ ใช้ตำแหน่งปัจจุบัน บันทึกเมืองโปรด และรับคำแนะนำด้านสุขภาพภาษาไทยที่สอดคล้องกับสถานการณ์ล่าสุดได้ทันที

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![OpenWeather](https://img.shields.io/badge/OpenWeather-EB6E4B?style=for-the-badge&logo=OpenWeatherMap&logoColor=white)](https://openweathermap.org/api)
[![Gemini API](https://img.shields.io/badge/Gemini_API-34A853?style=for-the-badge&logo=google-gemini&logoColor=white)](https://ai.google.dev/)

[🚀 **Live Demo** 🚀](https://weatherairquality.onrender.com/)
&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;
[🔗 **สไลด์นำเสนอ (Canva)** 🔗](https://www.canva.com/design/DAG1HiTYYfY/m_5jj2O4Dt3d14G7PwpxnA/view?utm_content=DAG1HiTYYfY&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=hbca9533057)
</div>

## ✨ ทีมพัฒนา (Development Team)

| บทบาท | ชื่อ |
| :--- | :--- |
| 👨‍💻 **Core Developer** | สรวิชญ์ ศาสนสุพินธุ์ |
| 🧑‍💼 **Project Manager** | ศิขรินทร์ อุปจันทร์ |
| 🧪 **Automated Tester** | แทนคุณ พันธ์นิกุล |

<br>

## 🎬 ตัวอย่างการใช้งาน (Demo)

🎥 **[คลิกเพื่อชมวิดีโอ Walkthrough การใช้งาน (Google Drive)](https://drive.google.com/file/d/1brdQVO9sTr4nuFuRvTa7jZ97hU6YEz_L/view?usp=sharing)**

![Demo GIF](https://github.com/Bigzzz0/weatherairquality/blob/main/static/Gif%20demo.gif)
[🚀 **Live Demo** 🚀](https://weatherairquality.onrender.com/)
## 🌟 คุณลักษณะเด่น (Features)

-   **ภาพรวมสภาพอากาศปัจจุบัน** – แสดงอุณหภูมิ ความชื้น ความเร็ว/ทิศทางลม เวลา Sunrise & Sunset และสัญลักษณ์สภาพอากาศจาก OpenWeather API
-   **ติดตามคุณภาพอากาศ (AQI)** – ใช้ Air Pollution API ของ OpenWeather เพื่อบอกค่า AQI, ความเข้มข้นของมลพิษ และปรับโทนสี UI ตามระดับความเสี่ยง
-   **พยากรณ์ 5 วัน** – แสดงการ์ดสรุปอุณหภูมิสูง-ต่ำและแนวโน้มสภาพอากาศล่วงหน้าอย่างเข้าใจง่าย
-   **เมืองโปรด** – บันทึกเมืองที่เข้าชมบ่อยลงในฐานข้อมูล SQLite และเรียกดูได้ด้วยคลิกเดียว
-   **คำแนะนำสุขภาพจาก Gemini (ภาษาไทย)** – ส่งข้อมูลสภาพอากาศและ AQI ไปยัง Gemini API เพื่อสร้างคำแนะนำกิจกรรมและการดูแลสุขภาพเป็นภาษาไทย
-   **ส่วนติดต่อผู้ใช้แบบ Responsive** – ออกแบบด้วย Tailwind CSS รองรับทั้งหน้าจอมือถือและเดสก์ท็อป

## 🛠️ สิ่งที่ต้องเตรียม (Prerequisites)

-   Python 3.10 ขึ้นไป
-   [คีย์ OpenWeather API](https://home.openweathermap.org/users/sign_up)
-   [คีย์ Google Gemini API](https://aistudio.google.com/) (สำหรับคำแนะนำสุขภาพ)

## 🚀 ขั้นตอนการติดตั้ง (Installation)

1.  **โคลนโปรเจกต์**
    ```bash
    git clone <repository-url>
    cd weatherairquality
    ```

2.  **สร้างและเปิดใช้งาน Virtual Environment (แนะนำ)**
    ```bash
    # บน macOS/Linux
    python -m venv .venv
    source .venv/bin/activate

    # บน Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **ติดตั้งไลบรารีที่ต้องใช้**
    ```bash
    pip install -r requirements.txt
    ```

4.  **ตั้งค่าตัวแปรสภาพแวดล้อม (Environment Variables)**

    สร้างไฟล์ `.env` ที่รูทของโปรเจกต์แล้วใส่ค่าดังนี้:
    ```env
    API_KEY=<your_openweather_api_key>
    GEMINI_API_KEY=<your_gemini_api_key>
    ```

    > **หมายเหตุ:** ใน `main.py` มีคีย์ Gemini ตัวอย่างเพื่อการพัฒนาเท่านั้น ควรเปลี่ยนเป็นคีย์ของคุณเองหรือโหลดจากตัวแปรสภาพแวดล้อมก่อนใช้งานจริงเพื่อความปลอดภัย

5.  **เตรียมฐานข้อมูล (สำหรับการรันครั้งแรก)**

    เมื่อเริ่มเซิร์ฟเวอร์ครั้งแรก ระบบจะสร้างไฟล์ `database.db` และตาราง `favorites` ให้อัตโนมัติ หากต้องการเริ่มใหม่ให้ลบไฟล์ `database.db` แล้วรันเซิร์ฟเวอร์อีกครั้ง

## 🏃 การรันแอปพลิเคชัน (Running the Application)

```bash
python main.py
```

ดีฟอลต์เซิร์ฟเวอร์จะเปิดที่ `http://127.0.0.1:8080/` (หรือ `0.0.0.0:8080` เมื่อรันใน Codespaces/คอนเทนเนอร์)

## 🐳 การรันด้วย Docker (Running with Docker)

1.  **สร้างอิมเมจ (Build the image)**

    ```bash
    docker build -t weather-aqi-dashboard .
    ```

2.  **รันคอนเทนเนอร์ (Run the container)**

    ```bash
    docker run -p 8080:8080 \
      -e API_KEY=<your_openweather_api_key> \
      -e GEMINI_API_KEY=<your_gemini_api_key> \
      weather-aqi-dashboard
    ```

    หากต้องการเก็บฐานข้อมูลนอกคอนเทนเนอร์สามารถแม็ปโวลุ่มเพิ่มเติม เช่น `-v $(pwd)/database.db:/app/database.db`.

## 🐙 การรันด้วย Docker Compose และการ Deploy ขึ้น Render

ไฟล์ `docker-compose.yml` ได้ถูกเตรียมไว้เพื่อช่วยให้การรันหลายบริการและการตั้งค่าตัวแปรสภาพแวดล้อมทำได้สะดวกขึ้น ทั้งสำหรับการทดสอบบนเครื่องและเมื่อต้องนำไป Deploy บนแพลตฟอร์มคลาวด์อย่าง Render

### รันด้วย Docker Compose บนเครื่อง

```bash
docker compose up --build
```

ค่าเริ่มต้นจะเปิดพอร์ต `8080` ภายในเครื่องของคุณ และอ่านตัวแปรสภาพแวดล้อม `API_KEY` และ `GEMINI_API_KEY` จาก shell ปัจจุบัน (หากต้องการสามารถสร้างไฟล์ `.env` ในโฟลเดอร์เดียวกัน และ Docker Compose จะอ่านค่าให้อัตโนมัติ)

### Deploy ไปยัง Render โดยใช้ Docker Compose

1. **เตรียมโค้ด** – push โปรเจกต์ (รวมถึง `Dockerfile` และ `docker-compose.yml`) ขึ้น GitHub หรือ GitLab
2. **สร้าง Web Service ใหม่** – เข้า Render Dashboard → New → Web Service → เลือกรีโพที่เตรียมไว้
3. **เลือก Environment** – เลือกเป็น **Docker** แล้ว Render จะตรวจจับ `Dockerfile` เพื่อ build อิมเมจ (ไม่ต้องระบุ command เพิ่ม เพราะกำหนดไว้ใน Dockerfile/Compose แล้ว)
4. **ตั้งค่าตัวแปรสภาพแวดล้อม** – เพิ่ม `API_KEY` และ `GEMINI_API_KEY` ในเมนู Environment Variables ของ Render (Render จะส่งค่าเหล่านี้เข้าไปในคอนเทนเนอร์ตามที่เรากำหนดไว้ใน Compose)
5. **Deploy** – กดสร้างบริการ Render จะทำการ build และ deploy อัตโนมัติทุกครั้งที่ push โค้ดใหม่

> 💡 หากต้องการใช้ `docker-compose.yml` โดยตรงกับ Render สามารถสร้างไฟล์ `render.yaml` เพื่ออ้างอิง Compose Stack ได้เช่นกัน แต่สำหรับโปรเจกต์นี้ การมี Dockerfile และเพิ่ม Environment Variables ตามขั้นตอนข้างต้นก็เพียงพอสำหรับการใช้งานทั่วไป

## 🎮 วิธีการใช้งาน (How to Use)

1.  **ค้นหาเมือง** ที่ต้องการผ่านช่องค้นหาหรือคลิก **📍 ใช้ตำแหน่งของฉัน** เพื่อดึงข้อมูลจาก geolocation ของเบราว์เซอร์
2.  **ตรวจสอบสภาพอากาศปัจจุบัน** และ **แผงคุณภาพอากาศ** ซึ่งจะเปลี่ยนสีพื้นหลังเมื่อคุณภาพอากาศไม่ดี
3.  **ดูพยากรณ์ล่วงหน้า 5 วัน** เพื่อวางแผนกิจกรรม
4.  เมื่อข้อมูลสภาพอากาศและ AQI พร้อม ระบบจะร้องขอ **คำแนะนำสุขภาพภาษาไทยจาก Gemini** ให้อัตโนมัติ
5.  **บันทึกเมืองโปรด** ด้วยปุ่ม **+ Fav** เมืองที่บันทึกไว้จะแสดงในรายการด้านข้างและสามารถลบได้จากหน้าเดียวกัน

## 🩺 การแก้ไขปัญหาเบื้องต้น (Troubleshooting)

-   **แสดงผลข้อมูลไม่ได้หรือว่างเปล่า:** ตรวจสอบว่า OpenWeather API Key ถูกต้องและยังไม่หมดโควตา
-   **ไม่มีคำแนะนำจาก AI:** ตรวจสอบว่าตั้งค่า Gemini API Key แล้ว และบริการเปิดให้ใช้งานในภูมิภาคของคุณ
-   **เบราว์เซอร์ปฏิเสธตำแหน่งที่ตั้ง:** พิมพ์ชื่อเมืองเองหรืออนุญาตสิทธิ์การเข้าถึงตำแหน่งให้เบราว์เซอร์
-   **ฐานข้อมูลล็อก:** ปิดเซิร์ฟเวอร์แล้วลบไฟล์ `database.db` ก่อนเริ่มใหม่

#### ⚠️ ข้อควรระวัง: "Error fetching weather data" แต่ API Key ถูกต้อง

หากขึ้นข้อความนี้ทั้งที่ API Key ถูกต้อง อาจเกิดจากสาเหตุต่อไปนี้:
-   **ชื่อเมืองสะกดผิด** หรือไม่มีในฐานข้อมูล OpenWeather (ลองใช้ชื่อภาษาอังกฤษหรือชื่อเมืองหลัก)
-   **API Key ถูกบล็อกชั่วคราว** จากการเรียกใช้งานบ่อยเกินไป (รอ 1-2 นาทีแล้วลองใหม่)
-   **ปัญหาอินเทอร์เน็ตหรือ Firewall** ของเครื่องหรือเครือข่ายบล็อกการเชื่อมต่อไปยัง OpenWeather
-   **API Endpoint เปลี่ยนแปลง** หรือมีการอัปเดตจาก OpenWeather (ตรวจสอบ [สถานะ OpenWeather](https://openweathermap.statuspage.io/))
-   **ระบบปฏิบัติการ/เซิร์ฟเวอร์มีปัญหา DNS** (ลองรีสตาร์ทเครื่องหรือเปลี่ยน DNS)

> **💡 Tip:** สามารถดูรายละเอียด error จริงใน log ของ Flask ที่แสดงในเทอร์มินัล เพื่อช่วยวิเคราะห์ปัญหาได้แม่นยำขึ้น

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```

weatherairquality/
├── 📂 static/
│   └── (ไฟล์ รูปภาพ)
├── 📂 templates/
│   └── 📄 index.html      # UI แดชบอร์ดที่ใช้ Tailwind และสคริปต์ฝั่งไคลเอนต์
├── 📄 main.py             # เส้นทาง Flask และตรรกะเชื่อมต่อบริการต่าง ๆ
├── 📄 requirements.txt    # รายการไลบรารีของ Python
├── 📄 database.db         # ฐานข้อมูล SQLite (สร้างเมื่อรันแอป)
├── 📄 .env                # ไฟล์เก็บ API keys (ไม่ควรอยู่ใน Git)
├── 📄 README.md           # เอกสารประกอบโปรเจกต์ (ไฟล์นี้)
└── 📄 test_main.py        # ไฟล์สำหรับทดสอบโปรแกรม (Automated Tests)
```
