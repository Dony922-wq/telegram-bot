import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8882480132:AAEvS7IF-00mXJ2P-ySbD_Xyr4ZiJ7yfOOk"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url or not url.startswith("http"):
        return

    await update.message.reply_text("⏳ جاري تحليل الرابط وتحميل المقاطع، قليلاً من الوقت...")

    output_template = "downloaded_video.mp4"
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio',
        'outtmpl': output_template,
        'max_filesize': 50 * 1024 * 1024,
        'geo_bypass': True,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_template):
            with open(output_template, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption="✅ تم التنزيل بنجاح بواسطة البوت.")
            os.remove(output_template)
        else:
            await update.message.reply_text("❌ عذراً، لم أتمكن من العثور على ملف الفيديو للتحميل.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحميل: تأكد أن الرابط عام وصحيح.")
        if os.path.exists(output_template):
            os.remove(output_template)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 البوت يعمل الآن ويستمع للروابط...")
    app.run_polling()

if __name__ == '__main__':
    main()
