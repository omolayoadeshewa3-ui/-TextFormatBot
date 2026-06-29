import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests

# ============= LOGGING SETUP =============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= ENVIRONMENT VARIABLES =============
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'WordTranslate1Bot')
BOT_NAME = os.environ.get('BOT_NAME', 'WordTranslate1Bot')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN is required. Add it to Railway variables.")

logger.info(f"✅ Starting {BOT_NAME} (@{BOT_USERNAME})")

# ============= LANGUAGE CONFIGURATION =============
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
    'tr': 'Turkish',
    'nl': 'Dutch',
    'pl': 'Polish',
    'vi': 'Vietnamese',
    'th': 'Thai'
}

LANGUAGE_FLAGS = {
    'en': '🇬🇧', 'es': '🇪🇸', 'fr': '🇫🇷', 'de': '🇩🇪',
    'it': '🇮🇹', 'pt': '🇵🇹', 'ru': '🇷🇺', 'zh': '🇨🇳',
    'ja': '🇯🇵', 'ko': '🇰🇷', 'ar': '🇸🇦', 'hi': '🇮🇳',
    'bn': '🇧🇩', 'ur': '🇵🇰', 'fa': '🇮🇷', 'tr': '🇹🇷',
    'nl': '🇳🇱', 'pl': '🇵🇱', 'vi': '🇻🇳', 'th': '🇹🇭'
}

# ============= USER DATA =============
user_data = {}

# ============= TRANSLATION FUNCTIONS =============

def translate_text(text, target_lang, source_lang='auto'):
    """Translate text using LibreTranslate API (free, no API key required)"""
    try:
        url = "https://libretranslate.com/translate"
        payload = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result.get('translatedText', text)
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None

def detect_language(text):
    """Detect language using LibreTranslate API"""
    try:
        url = "https://libretranslate.com/detect"
        payload = {'q': text}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result and len(result) > 0:
            detected = result[0]
            return detected.get('language'), detected.get('confidence', 0)
        return None, 0
    
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return None, 0

# ============= COMMAND HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    first_name = user.first_name or "User"
    
    welcome_text = (
        f"🌍 *Welcome to {BOT_NAME}, {first_name}!*\n\n"
        f"I'm @{BOT_USERNAME}, your language translator bot!\n\n"
        "🔄 *What I can do:*\n"
        "• Translate between 20+ languages\n"
        "• Auto-detect source language\n"
        "• Fast and accurate translations\n\n"
        "👇 *How to use:*\n"
        "1. Send me text to translate\n"
        "2. Select the target language\n"
        "3. Get your translation!\n\n"
        "📤 *Or use commands:*\n"
        "/translate - Translate text\n"
        "/detect - Detect language\n"
        "/languages - Show supported languages\n"
        "/about - About this bot"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 Translate Text", callback_data="translate"),
            InlineKeyboardButton("🔍 Detect Language", callback_data="detect"),
        ],
        [
            InlineKeyboardButton("🌐 All Languages", callback_data="languages"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    about_text = (
        "ℹ️ *About WordTranslateBot*\n\n"
        "🌍 Language Translator Bot\n\n"
        "🔄 *Features:*\n"
        "• Translate between 20+ languages\n"
        "• Auto language detection\n"
        "• Quick and accurate\n\n"
        "🌐 *Supported Languages:*\n"
        "English, Spanish, French, German,\n"
        "Italian, Portuguese, Russian, Chinese,\n"
        "Japanese, Korean, Arabic, Hindi,\n"
        "Bengali, Urdu, Persian, Turkish,\n"
        "Dutch, Polish, Vietnamese, Thai\n\n"
        "Made with ❤️ using Python"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        about_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command."""
    lang_text = "🌐 *Supported Languages:*\n\n"
    
    lang_list = list(LANGUAGES.items())
    for i in range(0, len(lang_list), 3):
        row = lang_list[i:i+3]
        row_text = "  ".join([f"{LANGUAGE_FLAGS.get(code, '')} {name}" for code, name in row])
        lang_text += f"{row_text}\n"
    
    lang_text += f"\n📊 *Total: {len(LANGUAGES)} languages*"
    lang_text += "\n\n📝 *How to use:*\n"
    lang_text += "Send me text, then select a target language!"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        lang_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /translate command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None}
    
    user_data[user_id]['action'] = 'translate'
    
    # Create language selection keyboard (2 columns)
    keyboard = []
    row = []
    lang_items = list(LANGUAGES.items())
    for i, (code, name) in enumerate(lang_items):
        flag = LANGUAGE_FLAGS.get(code, '')
        row.append(InlineKeyboardButton(f"{flag} {name}", callback_data=f"lang_{code}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 *Select target language:*\n\n"
        "Choose the language you want to translate to.\n"
        "Then send me the text to translate!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /detect command."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None}
    
    user_data[user_id]['action'] = 'detect'
    
    await update.message.reply_text(
        "🔍 *Language Detector*\n\n"
        "Send me text and I'll detect its language!\n\n"
        "📝 Send any text message.",
        parse_mode='Markdown'
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None, 'target_lang': 'en'}
    
    action = user_data[user_id].get('action', 'translate')
    target_lang = user_data[user_id].get('target_lang', 'en')
    
    if action == 'detect':
        # Detect language
        detected_lang, confidence = detect_language(text)
        
        if detected_lang and confidence > 0.5:
            lang_name = LANGUAGES.get(detected_lang, detected_lang)
            flag = LANGUAGE_FLAGS.get(detected_lang, '')
            confidence_percent = int(confidence * 100)
            
            response = (
                f"🔍 *Language Detection Result*\n\n"
                f"📝 Text: *{text[:100]}*{'...' if len(text) > 100 else ''}\n\n"
                f"🌐 Detected Language: {flag} *{lang_name}*\n"
                f"📊 Confidence: *{confidence_percent}%*"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Translate", callback_data="translate"),
                    InlineKeyboardButton("🔍 Detect Again", callback_data="detect"),
                ],
                [
                    InlineKeyboardButton("🔙 Menu", callback_data="menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            response = "❌ Could not detect the language with enough confidence. Please try again."
            await update.message.reply_text(response, parse_mode='Markdown')
        return
    
    elif action == 'translate':
        if not target_lang:
            await update.message.reply_text(
                "⚠️ Please select a target language first!\n"
                "Use /translate to choose a language."
            )
            return
        
        # Auto-detect source language
        detected_lang, _ = detect_language(text)
        source_lang = detected_lang if detected_lang else 'auto'
        
        # Translate
        processing_msg = await update.message.reply_text("⏳ Translating...")
        
        translated = translate_text(text, target_lang, source_lang)
        
        if translated:
            source_name = LANGUAGES.get(source_lang, 'Unknown')
            target_name = LANGUAGES.get(target_lang, 'Unknown')
            source_flag = LANGUAGE_FLAGS.get(source_lang, '')
            target_flag = LANGUAGE_FLAGS.get(target_lang, '')
            
            response = (
                f"🔄 *Translation Result*\n\n"
                f"📝 *Original:*\n{text}\n\n"
                f"🌐 {source_flag} {source_name} → {target_flag} {target_name}\n\n"
                f"📝 *Translated:*\n{translated}"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Translate Again", callback_data="translate"),
                    InlineKeyboardButton("🔍 Detect", callback_data="detect"),
                ],
                [
                    InlineKeyboardButton("🔙 Menu", callback_data="menu"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.delete()
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ Translation failed. Please try again."
            )
        return
    
    else:
        # Default: translate to English
        translated = translate_text(text, 'en')
        if translated:
            response = f"🔄 *Translation to English:*\n\n{translated}"
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "❌ Sorry, I couldn't translate that. Please try again."
            )


# ============= CALLBACK QUERY HANDLERS =============

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(query.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'action': None, 'target_lang': 'en'}
    
    # ===== MENU =====
    if data == "menu":
        keyboard = [
            [
                InlineKeyboardButton("🔄 Translate Text", callback_data="translate"),
                InlineKeyboardButton("🔍 Detect Language", callback_data="detect"),
            ],
            [
                InlineKeyboardButton("🌐 All Languages", callback_data="languages"),
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 *Welcome to WordTranslateBot!*\n\nWhat would you like to do?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== TRANSLATE =====
    elif data == "translate":
        user_data[user_id]['action'] = 'translate'
        
        keyboard = []
        row = []
        lang_items = list(LANGUAGES.items())
        for i, (code, name) in enumerate(lang_items):
            flag = LANGUAGE_FLAGS.get(code, '')
            row.append(InlineKeyboardButton(f"{flag} {name}", callback_data=f"lang_{code}"))
            if (i + 1) % 2 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 *Select target language:*\n\n"
            "Choose the language you want to translate to.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== DETECT =====
    elif data == "detect":
        user_data[user_id]['action'] = 'detect'
        await query.edit_message_text(
            "🔍 *Language Detector*\n\n"
            "Send me text and I'll detect its language!",
            parse_mode='Markdown'
        )
    
    # ===== LANGUAGES =====
    elif data == "languages":
        lang_text = "🌐 *Supported Languages:*\n\n"
        
        lang_list = list(LANGUAGES.items())
        for i in range(0, len(lang_list), 3):
            row = lang_list[i:i+3]
            row_text = "  ".join([f"{LANGUAGE_FLAGS.get(code, '')} {name}" for code, name in row])
            lang_text += f"{row_text}\n"
        
        lang_text += f"\n📊 *Total: {len(LANGUAGES)} languages*"
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            lang_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== ABOUT =====
    elif data == "about":
        about_text = (
            "ℹ️ *About WordTranslateBot*\n\n"
            "🌍 Language Translator Bot\n\n"
            "🔄 Translate between 20+ languages\n"
            "🔍 Auto language detection\n\n"
            "Made with ❤️ using Python"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            about_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ===== LANGUAGE SELECTION =====
    elif data.startswith('lang_'):
        target_lang = data.replace('lang_', '')
        user_data[user_id]['target_lang'] = target_lang
        
        lang_name = LANGUAGES.get(target_lang, target_lang)
        flag = LANGUAGE_FLAGS.get(target_lang, '')
        
        await query.edit_message_text(
            f"✅ *Selected: {flag} {lang_name}*\n\n"
            "Now send me the text to translate!\n\n"
            "📝 Send any text message.",
            parse_mode='Markdown'
        )


def main():
    """Start the bot."""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("about", about))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("detect", detect_command))
        
        # Callback handler
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler for text
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("🚀 Bot started successfully!")
        logger.info(f"📱 Bot username: @{BOT_USERNAME}")
        logger.info(f"🌐 Supported languages: {len(LANGUAGES)}")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
