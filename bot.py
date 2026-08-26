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

    # التحقق من أن الرابط خاص بتطبيق X (تويتر)
    if not any(domain in url for domain in ["twitter.com", "x.com"]):
        await update.message.reply_text("❌ هذا البوت مخصص لتنزيل مقاطع تطبيق X (تويتر) فقط.")
        return

    await update.message.reply_text("⏳ جاري تحليل رابط X وتحميل المقاطع...")

    output_template = "downloaded_video.mp4"
    ydl_opts = {
        'format': 'best',
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
                await update.message.reply_video(video=video_file, caption="✅ تم تنزيل فيديو X بنجاح.")
            os.remove(output_template)
        else:
            await update.message.reply_text("❌ عذراً، لم أتمكن من العثور على ملف الفيديو في الرابط.")
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء التحميل: تأكد أن التغريدة عامة وتحتوي على فيديو.")
        if os.path.exists(output_template):
            os.remove(output_template)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 بوت X يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
