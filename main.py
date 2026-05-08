import io
from io import BytesIO

import requests
import streamlit as st

import config
from groq import generate_response

from huggingface_hub import InferenceClient


MATH_SYSTEM = """
You are a Math Mastermind.

Solve with:
- clear step-by-step reasoning
- correct notation
- final answer clearly shown

Verify the answer when possible.
"""


CHAT_CSS = """
<style>

.wrap{
    max-height:520px;
    overflow-y:auto;
    padding-right:6px;
}

.card{
    border:1px solid #e6e6e6;
    background:#ffffff;
    border-radius:10px;
    padding:14px 16px;
    margin:10px 0;
    box-shadow:0 1px 2px rgba(0,0,0,0.04);
}

.q{
    font-weight:700;
    color:#0a6ebd;
    margin-bottom:8px;
}

.meta{
    display:inline-block;
    background:#FF9800;
    color:#fff;
    padding:2px 8px;
    border-radius:12px;
    font-size:12px;
    margin-left:8px;
}

.a{
    white-space:pre-wrap;
    color:#333;
    line-height:1.5;
}

</style>
"""


# =========================================================
# Export TXT
# =========================================================

def export_txt(history):

    txt = ""

    for i, h in enumerate(history, 1):

        txt += f"Q{i}: {h['question']}\n"

        if "difficulty" in h:
            txt += f"Difficulty: {h['difficulty']}\n"

        txt += f"A{i}: {h['answer']}\n\n"

    bio = io.BytesIO(txt.encode("utf-8"))
    bio.seek(0)

    return bio


# =========================================================
# AI Teaching Assistant
# =========================================================

def teaching_answer(question: str) -> str:

    return generate_response(
        question,
        temperature=0.3,
        max_tokens=1024
    )


def run_ai_teaching_assistance():

    st.title("AI Teaching Assistant")

    st.session_state.setdefault("history_ata", [])

    c1, c2 = st.columns([1, 2])

    if c1.button("Clear", key="c_ata"):
        st.session_state.history_ata = []
        st.rerun()

    if st.session_state.history_ata:

        c2.download_button(
            "Export",
            export_txt(st.session_state.history_ata),
            "AI_Teaching_Assistant.txt",
            "text/plain"
        )

    question = st.text_input(
        "Enter your question:",
        key="q_ata"
    )

    if st.button("Ask", key="a_ata"):

        if not question.strip():

            st.warning("Enter a question.")

        else:

            with st.spinner("Thinking..."):

                answer = teaching_answer(question.strip())

                st.session_state.history_ata.append({
                    "question": question.strip(),
                    "answer": answer
                })

            st.rerun()

    if not st.session_state.history_ata:
        return

    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    html = '<div class="wrap">'

    for i, qa in enumerate(st.session_state.history_ata, 1):

        html += f"""
        <div class="card">
            <div class="q">
                Q{i}: {qa["question"]}
            </div>

            <div class="a">
                {qa["answer"]}
            </div>
        </div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# =========================================================
# Math Mastermind
# =========================================================

def math_answer(question: str, level: str) -> str:

    prompt = f"""
{MATH_SYSTEM}

Difficulty: {level}

Math Problem:
{question}
"""

    return generate_response(
        prompt,
        temperature=0.1,
        max_tokens=1024
    )


def run_math_mastermind():

    st.title("🧮 Math Mastermind")

    st.session_state.setdefault("history_mm", [])
    st.session_state.setdefault("k_mm", 0)

    c1, c2 = st.columns([1, 2])

    if c1.button("🧹 Clear", key="c_mm"):

        st.session_state.history_mm = []
        st.rerun()

    if st.session_state.history_mm:

        c2.download_button(
            "📄 Export",
            export_txt(st.session_state.history_mm),
            "Math_Mastermind.txt",
            "text/plain"
        )

    with st.form("mm_form", clear_on_submit=True):

        question = st.text_area(
            "Math problem:",
            height=120,
            key=f"mm_{st.session_state.k_mm}"
        )

        a, b = st.columns([3, 1])

        submit = a.form_submit_button(
            "Solve",
            use_container_width=True
        )

        level = b.selectbox(
            "Level",
            ["Basic", "Intermediate", "Advanced"],
            index=1
        )

        if submit:

            if not question.strip():

                st.warning("Enter a problem.")

            else:

                with st.spinner("Solving..."):

                    answer = math_answer(
                        question.strip(),
                        level
                    )

                st.session_state.history_mm.insert(
                    0,
                    {
                        "question": question.strip(),
                        "answer": answer,
                        "difficulty": level
                    }
                )

                st.session_state.k_mm += 1
                st.rerun()

    if not st.session_state.history_mm:
        return

    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    html = '<div class="wrap">'

    for i, qa in enumerate(st.session_state.history_mm, 1):

        html += f"""
        <div class="card">

            <div class="q">
                Q{i}: {qa["question"]}
                <span class="meta">
                    {qa["difficulty"]}
                </span>
            </div>

            <div class="a">
                {qa["answer"]}
            </div>

        </div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# =========================================================
# Safe AI Image Generator
# =========================================================

def run_safe_ai_image_generator():

    FILTER_API_URL = "https://filters-zeta.vercel.app/api/filter"

    IMG_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

    img_client = InferenceClient(
        provider="hf-inference",
        api_key=config.HF_API_KEY
    )

    st.title("🎨 Safe AI Image Generator")

    def is_prompt_safe(prompt: str):

        try:

            response = requests.post(
                FILTER_API_URL,
                json={"text": prompt},
                timeout=15
            )

            if response.status_code != 200:

                return (
                    False,
                    f"Filter API failed: {response.status_code}"
                )

            data = response.json()

            if data.get("ok") is True:
                return True, None

            return (
                False,
                data.get("reason", "Unsafe prompt.")
            )

        except Exception as e:

            return False, f"Filter API error: {e}"

    def generate_image(prompt: str):

        safe, err = is_prompt_safe(prompt)

        if not safe:
            return None, err

        try:

            image = img_client.text_to_image(
                prompt=prompt,
                model=IMG_MODEL
            )

            return image, None

        except Exception as e:

            return None, f"Image generation error: {e}"

    with st.form("img_form"):

        prompt = st.text_area(
            "Image Description:",
            height=120
        )

        submit = st.form_submit_button(
            "Generate Image"
        )

    if submit:

        if not prompt.strip():

            st.warning("Enter a description.")

        else:

            with st.spinner("Generating image..."):

                image, err = generate_image(prompt.strip())

            if err:

                st.error(err)

            else:

                st.image(
                    image,
                    use_container_width=True
                )

                st.session_state.generated_image = image

    image = st.session_state.get("generated_image")

    if image:

        buf = BytesIO()

        image.save(buf, format="PNG")

        st.download_button(
            "Download Image",
            buf.getvalue(),
            "ai_generated_image.png",
            "image/png"
        )


# =========================================================
# Main
# =========================================================

def main():

    st.set_page_config(
        page_title="AI Multi Tool",
        page_icon="🤖",
        layout="centered"
    )

    st.sidebar.title("Choose AI Feature")

    option = st.sidebar.selectbox(
        "",
        [
            "AI Teaching Assistant",
            "Math Mastermind",
            "Safe AI Image Generator"
        ]
    )

    if option == "AI Teaching Assistant":

        run_ai_teaching_assistance()

    elif option == "Math Mastermind":

        run_math_mastermind()

    else:

        run_safe_ai_image_generator()


if __name__ == "__main__":
    main()
