import os
import random

from services.tips_provider import TipsProvider


class TraderTips(TipsProvider):

    def __init__(self):
        super().__init__(
            index_path=os.path.join(
                os.path.dirname(__file__), "../trader_tips.faiss.index"
            ),
            model="gpt-4-turbo",
            tip_type="trader",
            model_messages=[],
        )

    async def get_new_tip_content(self):
        level = random.choice(["Professional", "Basic", "Advanced"])
        self.model_messages = [
            {
                "role": "system",
                "content": (
                    "You are a Daily Trading Tips channel. "
                    "Format your response in this exact structure:\n"
                    "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                    "2. Add a brief explanation of the trading concept, strategy, or tip in bold\n"
                    "3. Provide practical examples or scenarios\n"
                    "4. Include relevant trading terminology\n"
                    "5. Add risk management considerations if applicable\n"
                    "6. Use emojis extensively in the text\n"
                    "7. Do not repeat the same tip\n"
                    "8. Keep it concise and practical"
                ),
            },
            {"role": "user", "content": f"Give me today's {level} trading tip."},
        ]
        return await super().get_new_tip_content()
