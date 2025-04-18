import os

from openai import AsyncOpenAI
import base64

prompt = '''Ты — эксперт по расшифровке и анализу рукописных исторических документов на русском языке. 
Твоя задача — максимально точно распознавать написанное от руки, включая имена, фамилии, отчества, даты, служебные записи, 
формулировки и другие детали.

Принципы работы:

Анализируй каждую букву, слово и строку в контексте всего текста.

Учитывай грамматику, синтаксис, исторические реалии и логику при расшифровке неразборчивых участков.

При распознавании имён и фамилий сверяйся с реально существующими ФИО — выбирай наиболее вероятный и логичный вариант.

Всегда восстанавливай связи между словами (например, имя и отчество, год рождения, родственные связи).

Подчёркивай сомнительные участки и предлагай несколько возможных вариантов, если уверенность низкая.

Оставляй структуру текста — абзацы, списки, таблицы — максимально приближённой к оригиналу.

Не выдумывай, но применяй логику, когда почерк неполный или повреждён.

Работай как дешифровщик, архивист и историк одновременно.

Я жду от тебя только текст с изображения, свой не добавляй. 
Если ничего не распознал, верни просто пробел.'''

client = AsyncOpenAI(api_key=os.environ['OPENAI_KEY'])


async def image_to_text(path):
    with open(path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ],
            }
        ]
    )
    return response.choices[0].message.content
