import os
import random

from services.tips_provider import TipsProvider


class JsTips(TipsProvider):

    def __init__(self):
        super().__init__(
            index_path=os.path.join(
                os.path.dirname(__file__), "../js_tips.faiss.index"
            ),
            model="gpt-4-turbo",
            tip_type="js",
            model_messages=[],
        )

    async def get_new_tip_content(self):
        level = random.choice(["Professional", "Basic", "Advanced"])
        js_or_ts = random.choice(["JavaScript", "TypeScript"])
        self.model_messages = [
            {
                "role": "system",
                "content": (
                    f"You are a Daily {js_or_ts} Tips channel. "
                    "Format your response in this exact structure:\n"
                    "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                    "2. Add a brief explanation of the tip in bold and then the next line\n"
                    "3. Always include a code example using this exact format:\n"
                    "```javascript\n"  # or typescript
                    "// Your code here\n"
                    "// Add comments with output if needed\n"
                    "```\n"
                    "4. Make sure code examples are practical and executable\n"
                    "5. Use proper formatting and indentation in code examples\n"
                    "6. Use emojis extensively in the text\n"
                    "7. Do not repeat the same tip\n"
                    "8. Include modern features and best practices"
                ),
            },
            {"role": "user", "content": f"Give me today's {level} {js_or_ts} tip."},
        ]
        return await super().get_new_tip_content()
