from openai import OpenAI
import config

GROQ_URL = "https://api.groq.com/openai/v1"

MODELS = config.GROQ_MODELS


def generate_response(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 512
):

    if not config.GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY missing"

    try:

        client = OpenAI(
            api_key=config.GROQ_API_KEY,
            base_url=GROQ_URL
        )

        last_error = None

        for model in MODELS:

            try:

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return response.choices[0].message.content

            except Exception as e:

                last_error = e

        return f"""
Groq model failed.

Models tried:
{MODELS}

Actual Error:
{type(last_error).__name__}

{last_error}
"""

    except Exception as e:

        return f"""
Groq client creation failed.

{type(e).__name__}: {e}
"""
        
