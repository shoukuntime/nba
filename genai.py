import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# 設定Gemini API 密鑰
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

#連接GEMINI模型
model = genai.GenerativeModel('gemini-1.5-flash')
def get_info(titles,datas,sentence):
    response = model.generate_content(f"{titles}{datas}{sentence}，並回傳繁體中文，請把**改成html語法，並且把**和```html刪掉，不要寫無關資訊")
    return response.text