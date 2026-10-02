import requests
import os
from dotenv import load_dotenv

# بارگذاری توکن
load_dotenv()
TOKEN = os.getenv("BALE_BOT_TOKEN")

# شناسه عددی شما در بله
CHAT_ID = "2106622428"
URL = f"https://tapi.bale.ai/bot{TOKEN}/sendPhoto"
WELCOME_IMAGE = os.path.join(os.path.dirname(__file__), "media", "welcome.jpg")

print("در حال آپلود فایل، لطفاً صبر کنید...")

with open(WELCOME_IMAGE, "rb") as image_file:
    response = requests.post(
        URL,
        data={"chat_id": CHAT_ID},
        files={"photo": image_file}
    )

data = response.json()
if data.get("ok"):
    # استخراج file_id از پاسخ سرور
    file_id = data["result"]["photo"][-1]["file_id"]
    print(f"\n✅ آپلود موفقیت‌آمیز بود!")
    print(f"File ID شما این است:\n{file_id}")
else:
    print(f"\n❌ خطا در آپلود: {data}")