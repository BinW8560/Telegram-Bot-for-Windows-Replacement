import logging
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Set your Telegram bot token
TELEGRAM_BOT_TOKEN = "YOUR TOKEN"

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Load the Products Information
def load_products(file_path):
    """Loads product information from a file."""
    products = pd.read_csv(file_path, sep='|', skipinitialspace=True, engine='python')
    products.columns = [col.strip() for col in products.columns]
    return products

# Recommend Products
def recommend_products(user_answers, products):
    """Recommends three products based on user answers."""
    translation_map = {
        "plastic": "Kunststoff",
        "wood": "Holz",
        "wood_aluminum": "Kunststoff-Alu-Fenster",
        "double": "2-fach",
        "triple": "3-fach",
        "average": "Basissicherheit",
        "high": "Erhöhte Beschlagsicherheit",
    }

    window_type = translation_map.get(user_answers.get('window_type', ''), '')
    filtered = products[
        products['Material'].str.contains(window_type, case=False, na=False)
    ]

    price_range = user_answers.get('price_range')
    if price_range == "0_100":
        filtered = filtered[filtered['Preis [€]'] <= 100]
    elif price_range == "100_200":
        filtered = filtered[(filtered['Preis [€]'] > 100) & (filtered['Preis [€]'] <= 200)]
    elif price_range == "over_200":
        filtered = filtered[filtered['Preis [€]'] > 200]

    glazing = translation_map.get(user_answers.get('glazing_type', ''), '')
    if glazing:
        filtered = filtered[filtered['Standard Verglasung'].str.contains(glazing, case=False, na=False)]

    depth = user_answers.get('window_recess_depth')
    if depth:
        filtered['Bautiefe'] = filtered['Bautiefe'].str.extract(r'(\d+)').astype(float)
        filtered = filtered[filtered['Bautiefe'] >= float(depth)]

    security = translation_map.get(user_answers.get('security_standard', ''), '')
    if security:
        filtered = filtered[filtered['Standard Sicherheit'].str.contains(security, case=False, na=False)]

    return filtered[['Produkt', 'Material', 'Preis [€]', 'Link']].head(3)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the bot and ask the first question."""
    context.user_data['answers'] = {}
    await ask_insulation_standard(update)

# Ask about insulation standard
async def ask_insulation_standard(update: Update) -> None:
    question = "What is the insulation standard of your building?"
    keyboard = [
        [InlineKeyboardButton("Poor", callback_data="insulation_poor")],
        [InlineKeyboardButton("Average", callback_data="insulation_average")],
        [InlineKeyboardButton("High", callback_data="insulation_high")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

# Callback query handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data
    answers = context.user_data['answers']

    if choice.startswith("insulation_"):
        answers['insulation_standard'] = choice.split("_")[1]
        await query.message.reply_text("Which type of windows do you prefer?")
        await ask_window_type(query)

    elif choice.startswith("material_"):
        answers['window_type'] = choice.split("_")[1]
        await query.message.reply_text("What price range are you willing to accept per window?")
        await ask_price_range(query)

    elif choice.startswith("price_"):
        answers['price_range'] = choice.split("_", 1)[1]
        await query.message.reply_text("What type of glazing do you prefer?")
        await ask_glazing_type(query)

    elif choice.startswith("glazing_"):
        answers['glazing_type'] = choice.split("_")[1]
        await query.message.reply_text("What is the depth (in cm) of the window recess for installation?")
        context.user_data['next_question'] = "depth"

    elif choice.startswith("security_"):
        answers['security_standard'] = choice.split("_")[1]
        recommendations = recommend_products(answers, products)
        if not recommendations.empty:
            await query.message.reply_text(
                "Thank you for your responses! Here are your recommendations:\n\n" +
                recommendations.to_string(index=False)
            )
        else:
            await query.message.reply_text("No products match your criteria. Please try again with different inputs.")

# Handle user messages for depth
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answers = context.user_data['answers']
    next_question = context.user_data.get('next_question')

    if next_question == "depth":
        try:
            depth = float(update.message.text)
            answers['window_recess_depth'] = depth
            context.user_data['next_question'] = None
            await ask_security_standard(update)
        except ValueError:
            await update.message.reply_text("Please provide a valid numeric value for depth (e.g., 20.5).")
    else:
        await update.message.reply_text("I'm sorry, I didn't understand that.")

# Ask about window type
async def ask_window_type(query):
    keyboard = [
        [InlineKeyboardButton("Wood", callback_data="material_wood")],
        [InlineKeyboardButton("Wood-Aluminum", callback_data="material_wood_aluminum")],
        [InlineKeyboardButton("Plastic", callback_data="material_plastic")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Choose your window type:", reply_markup=reply_markup)

# Ask about price range
async def ask_price_range(query):
    keyboard = [
        [InlineKeyboardButton("€0–100", callback_data="price_0_100")],
        [InlineKeyboardButton("€100–200", callback_data="price_100_200")],
        [InlineKeyboardButton("> €200", callback_data="price_over_200")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Choose your price range:", reply_markup=reply_markup)

# Ask about glazing type
async def ask_glazing_type(query):
    keyboard = [
        [InlineKeyboardButton("Double glazing", callback_data="glazing_double")],
        [InlineKeyboardButton("Triple glazing", callback_data="glazing_triple")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Choose your glazing type:", reply_markup=reply_markup)

# Ask about security standard
async def ask_security_standard(update: Update) -> None:
    question = "What is the security standard you prefer?"
    keyboard = [
        [InlineKeyboardButton("Average", callback_data="security_average")],
        [InlineKeyboardButton("High", callback_data="security_high")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

# Main function to run the bot
def main():
    global products
    file_path = "products.txt"
    products = load_products(file_path)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
