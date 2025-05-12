import os
import random

from services.tips_provider import TipsProvider


class BlockchainTips(TipsProvider):

    def __init__(self):
        super().__init__(
            index_path=os.path.join(
                os.path.dirname(__file__), "../blockchain_tips.faiss.index"
            ),
            model="gpt-4-turbo",
            tip_type="blockchain",
            model_messages=[],
        )

    async def get_new_tip_content(self):
        level = random.choice(["Professional", "Basic", "Advanced"])
        with_code = random.choice([True, False])
        if with_code:
            system_msg = (
                "You are a Daily Blockchain Tricks channel. "
                "Format your response in this exact structure:\n"
                "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                "2. Add a brief explanation of the tip in bold and then the next line.\n"
                "3. Always include a code example using this exact format:\n"
                "```solidity\n"
                "// Your code here\n"
                "// Add comments with output if needed\n"
                "```\n"
                "4. Do not add any additional text after the code example\n"
                "5. Use emojis extensively in the text\n"
                "6. Do not repeat the same tip"
            )
        else:
            system_msg = (
                "You are a Daily Blockchain Tricks channel. "
                "Format your response in this exact structure:\n"
                "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                "2. Add a brief explanation of the tip in bold and then the next line.\n"
                "3. Use emojis extensively in the text\n"
                "4. Do not repeat the same tip"
            )
        self.model_messages = [
            {
                "role": "system",
                "content": system_msg,
            },
            {
                "role": "user",
                "content": f"Give me today's {level} Blockchain tip. Ensure it is unique.",
            },
        ]
        return await super().get_new_tip_content()
