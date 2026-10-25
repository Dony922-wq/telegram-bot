
import os
import re
import asyncio
import logging
from io import BytesIO

import yt_dlp
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("8790107411:AAERI47KWloR0aGsAyAurcsLAgmAlDjaJ2M", "")

MAX_RESULTS = 100

EXCLUDE_WORDS = [
    "حفلة", "حفلات", "حفل", "حفله",
    "جلسة", "جلسات", "جلسه",
    "ابتزاز",
    "مقابلة", "مقابلات", "مقابله",
    "كواليس", "كاريوكي", "karaoke",
    "ريمكس", "remix", "ميكس", "مكس",
    "لايف", "live", "concert",
    "حفلة كاملة", "مسرح", "reaction",
    "بطيء", "slow", "رد فعل",
]

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def unwanted(title):
    text = title.casefold()
    return any(word.casefold() in text for word in EXCLUDE_WORDS)


def clean_title(title):
    # حذف أرقام الترتيب والرموز الشائعة للمقارنة
    title = re.sub(r"^\s*\d+[\s._-]+", "", title)
    title = re.sub(r"[^\w]", "", title.casefold())
    return title


def search_songs(artist):
    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": MAX_RESULTS,
    }

    query = f"ytsearch{MAX_RESULTS}:{artist} official audio"

    with yt_dlp.YoutubeDL(options) as ydl:
        data = ydl.extract_info(query, download=False)

    songs = []
    seen = set()

    for item in data.get("entries") or []:
        if not item:
            continue

        title = (item.get("title") or "").strip()
        url = item.get("url") or item.get("webpage_url") or ""

        if not title or unwanted(title):
            continue

        # نستخدم رابط يوتيوب عند توفر معرّف الفيديو
        video_id = item.get("id")
        if video_id:
            url = f"https://www.youtube.com/watch?v={video_id}"

        if not url.startswith("https://"):
            continue

        key = clean_title(title)
        if not key or key in seen:
            continue

        seen.add(key)
        songs.append({"title": title, "url": url})

    return songs


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🎵 DJ HAMAD\n\n"
        "أرسل اسم المغني للبحث عن أغانيه.\n"
        "مثال: ماجد المهندس\n\n"
        "سأستبعد عناوين الحفلات والجلسات والريمكس "
        "والمقابلات وابتزاز."
    )


async def handle_artist(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    artist = (update.message.text or "").strip()

    if not artist or len(artist) > 100:
        await update.message.reply_text(
            "اكتب اسم مغنٍ صحيحًا، بحد أقصى 100 حرف."
        )
        return

    status = await update.message.reply_text(
        f"🔎 أبحث عن: {artist}\nانتظر قليلًا..."
    )

    try:
        songs = await asyncio.to_thread(search_songs, artist)

        if not songs:
            await status.edit_text(
                "ما لقيت نتائج مناسبة. جرّب كتابة الاسم بطريقة أخرى."
            )
            return

        output = [
            f"DJ HAMAD - {artist}",
            f"عدد النتائج: {len(songs)}",
            "",
        ]

        for number, song in enumerate(songs, start=1):
            output.append(
                f"{number:03d} - {song['title']}"
            )
            output.append(song["url"])
            output.append("")

        content = "\n".join(output)
        filename = re.sub(
            r'[<>:"/\\|?*\n\r]', "_", artist
        )[:70] or "songs"

        buffer = BytesIO(content.encode("utf-8"))
        buffer.name = f"{filename}.txt"

        await status.edit_text(
            f"✅ انتهى البحث عن {artist}\n"
            f"عدد النتائج: {len(songs)}\n"
            "أرفقت لك قائمة الأغاني مرتبة بالأرقام."
        )

        await update.message.reply_document(
            document=InputFile(buffer, filename=buffer.name),
            caption=f"🎵 قائمة أغاني {artist}",
        )

    except Exception:
        logger.exception("Search failed")
        await status.edit_text(
            "❌ تعذر البحث الآن. حاول مرة ثانية لاحقًا."
        )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Telegram update failed",
        exc_info=context.error,
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "أضف TELEGRAM_BOT_TOKEN في إعدادات الاستضافة."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_artist,
        )
    )
    app.add_error_handler(error_handler)

    logger.info("DJ HAMAD bot starting")
    app.run_polling()


if __name__ == "__main__":
    main()
