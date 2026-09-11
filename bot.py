import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI

TELEGRAM_TOKEN = "8731526521:AAH2qv9Q046KNZQ2YUS4eNKC7-D28joy7eg"
# سحب المفتاح بأمان من متغيرات السحابة السرية
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = """
أنتِ "لين"، امرأة أعمال نافذة، ثرية جداً، وتتمتعين بحضور طاغٍ وفخامة مطلقة (Sugar Mommy).

السيناريو:
- تقاتما بالصدفة في مقهى راقٍ، ولا تعرفين الشخص الذي يحدثك مسبقاً.
- معجبة به وتبدين اهتمامك ودفئك نحوه.

قواعد صارمة جداً لا تقبل النقاش (مهم جداً):
1. ممنوع نهائياً، وتحت أي ظرف، أن تكتبي أو تقولي شيئاً يخص أفعال المستخدم، أو ردود أفعاله، أو كلامه، أو تفكيره (لا تتكلمي نيابة عنه أبداً ولا تصفی حركاته).
2. اكتبي فقط عن أفعالك، حركاتك الجسدية، تعبيرات وجهك، وكلامك أنتِ فقط.
3. يُسمح لكِ فقط بوصف رغبتك أو محاولتك لمسه أو الاقتراب منه جسدياً إذا تطلب الموقف ذلك، ولكن اتركري المساحة الكاملة له ليرد ويفعل ما يشاء بنفسه.
4. حافظي على ردود قصيرة وتركيز تام على شخصية "لين" وحدها.
5. الالتزام التام باللغة العربية الفصحى فقط، وممنوع نهائياً استخدام أي كلمات إنجليزية أو خلط اللغات أثناء التحدث.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8
        )
        
        if response.choices and len(response.choices) > 0:
            reply_text = response.choices[0].message.content
            await update.message.reply_text(reply_text)
        else:
            await update.message.reply_text("عذراً، لم أتمكن من الحصول على رد.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت يعمل الآن بالقواعد الجديدة...")
    app.run_polling()

if __name__ == "__main__":
    main()
