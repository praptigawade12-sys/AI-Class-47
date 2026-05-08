import config
from huggingface_hub import InferenceClient

MODELS = getattr(
    config,
    "HF_MODELS",
    ["meta-llama/Llama-3.1-8B-Instruct"]
)


def generate_response(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 512
) -> str:

    key = getattr(config, "HF_API_KEY", None)

    if not key:
        return "Error: HF_API_KEY missing"

    last_err = None

    for model in MODELS:
        try:
            client = InferenceClient(
                model=model,
                token=key
            )

            response = client.chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content

        except Exception as e:
            last_err = e

    return (
        "Hugging Face model failed.\n"
        f"Tried models: {MODELS}\n"
        f"Details: {type(last_err).__name__}: {last_err}"
    )
