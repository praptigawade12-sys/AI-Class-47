import config
from openai import OpenAI

GROQ_URL = "https://api.groq.com/openai/v1"
MODELS = getattr(config,"GROQ_MODELS",["llama-3.3-70b-versatile"])

def generate_response(prompt: str, temperature: float =0.3, max_tokens: int = 512) -> str:
    key = getattr(config, "GROQ_API_KEY",None)
    if not key:
        return "Error: GROQ_API_KEY missing in groq.py"
    c = OpenAI(api_key=key, base_url=GROQ_URL)

    last_err = None
    for m in MODELS:
        try:
            r = c.chat.completions.create(
                model=m,
                messages=[{"role":"user","content":prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return r.choices[0].message.content
        except Exception as e:
            last_err = e
    return(
        "Groq model failed. \n"
        f"Tried models: {MODELS}\n"
        f"Details: {type(last_err),__name__}: {last_err}"
    )