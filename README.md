Overview
This Python script is a Telegram bot that assists users in selecting windows based on their preferences and building requirements. It uses an interactive question-answer format to recommend suitable products from a pre-loaded dataset.

Features
Interactive User Experience:
Users are guided through a series of questions about their preferences, such as window material, price range, glazing type, and security standards.
Dynamic Recommendations:
Based on user inputs, the bot recommends up to three matching products from the dataset.
Flexible Input Handling:
Supports both button-based responses and free-text inputs (e.g., for window recess depth).
Product Data Integration:
The script reads product data from a text file (products.txt) for real-time recommendations.
Requirements
Python Libraries:
telegram
telegram.ext
pandas
logging
Telegram Bot Token:
Replace TELEGRAM_BOT_TOKEN with your bot's API token.
Data File:
A file named products.txt containing window product details in a pipe-separated format.
