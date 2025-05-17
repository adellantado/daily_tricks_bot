# 🗞 Daily Tips and Tricks

A Telegram bot that generates and sends daily tips and tricks to specific channels using OpenAI's GPT-4-turbo.

## Features

- **Automated Tip Generation**: Uses OpenAI's GPT-4-turbo to generate daily tips.
- **Unique Content**: Ensures tips are unique by leveraging FAISS for similarity checks.
- **Multi-Channel Support**: Sends tips to dedicated Telegram channels for Python, JavaScript/TypeScript, Blockchain and Trading.
- **Customizable Levels**: Tips are categorized into Basic, Advanced, and Professional levels.

## Channels

- 🐍 **Python Daily**: Tips and tricks for Python developers.
https://t.me/python_daily_tricks

- 🐸 **JS Daily**: Insights and best practices for JavaScript/TypeScript.
https://t.me/javascript_daily_tricks

- 💸 **Trader Daily**: Strategies and concepts for traders.
https://t.me/trader_daily_tricks

- 🔗 **Blockchain Daily**: Tips and tricks for Blockchain developers.
https://t.me/blockchain_daily_tricks

## Setup

1. Clone the repository.
2. Install dependencies from `requirements.txt`.
3. Configure environment variables in `.env` (see `.env.example` for reference).
4. Run the bot to start sending tips to your channels.