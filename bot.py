import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from openai import OpenAI

TELEGRAM_TOKEN = "8731526521:AAH2qv9Q046KNZQ2YUS4eNKC7-D28joy7eg"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# البرومبت الأساسي الافتراضي
DEFAULT_SYSTEM_PROMPT = """
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

# تخزين المحادثات والبرومبت لكل مستخدم ديناميكياً
user_prompts = {}
user_histories = {}

async def set_prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    new_prompt = " ".join(context.args)
    
    if not new_prompt:
        await update.message.reply_text("الرجاء كتابة التعليمات الجديدة بعد الأمر. مثال:\n/تعليمات أنتِ الآن شخصية صارمة...")
        return
    
    user_prompts[user_id] = new_prompt
    user_histories[user_id] = [] # تصفير الذاكرة مع التعليمات الجديدة
    await update.message.reply_text("تم تحديث تعليمات وشخصية لين بنجاح!")

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("تم مسح الذاكرة بنجاح، نبدأ من جديد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # جلب التعليمات الخاصة بالمستخدم أو استخدام الافتراضية
    current_system_prompt = user_prompts.get(user_id, DEFAULT_SYSTEM_PROMPT)
    
    # تهيئة الذاكرة للمستخدم لو لم تكن موجودة
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # إضافة رسالة المستخدم للذاكرة
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    # بناء رسائل الـ API مع النظام والذاكرة السابقة
    messages = [{"role": "system", "content": current_system_prompt}] + user_histories[user_id]
    
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            temperature=0.8
        )
        
        if response.choices and len(response.choices) > 0:
            reply_text = response.choices[0].message.content
            # حفظ رد البوت في الذاكرة لضمان استمرارية السياق
            user_histories[user_id].append({"role": "assistant", "content": reply_text})
            await update.message.reply_text(reply_text)
        else:
            await update.message.reply_text("عذراً، لم أتمكن من الحصول على رد.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # إضافة الأوامر باللغة العربية
    app.add_handler(CommandHandler("تعليمات", set_prompt_command))
    app.add_handler(CommandHandler("مسح", reset_command))
    
    # استقبال الرسائل النصية العادية
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("البوت يعمل الآن بالأوامر العربية...")
    app.run_polling()

if __name__ == "__main__":
    main()
