import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MAX_CHARS = 5000
DEFAULT_MODEL = "gpt-6.1-sol"
LANGUAGES = {
    "영어": "English",
    "일본어": "Japanese",
    "중국어": "Chinese (Simplified)",
}


def get_setting(name: str, default: str | None = None) -> str | None:
    """환경변수 -> st.secrets 순으로 설정값 조회."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def translate(text: str, target_language: str) -> str:
    api_key = get_setting("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    model = get_setting("OPENAI_MODEL", DEFAULT_MODEL)

    client = OpenAI(api_key=api_key, timeout=30)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a professional translator. Translate the user's text into "
                    f"{target_language}. Output only the translation, with no explanations "
                    f"or quotes. Preserve meaning, tone, line breaks, and formatting."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


CSS = """
<style>
:root {
  --bg: #F5F5F7; --card: #FFFFFF; --text: #1D1D1F; --sub: #6E6E73;
  --blue: #0071E3; --blue-hover: #0062C4; --line: rgba(0,0,0,.08);
  --shadow: 0 4px 24px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000; --card: #1C1C1E; --text: #F5F5F7; --sub: #A1A1A6;
    --line: rgba(255,255,255,.12); --shadow: 0 4px 24px rgba(0,0,0,.5);
  }
}
html, body, [class*="st-"], .stApp {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Pretendard",
               "Noto Sans KR", "Malgun Gothic", sans-serif;
}
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
.block-container { max-width: 720px; padding-top: 4rem; padding-bottom: 4rem; }

.hero { text-align: center; margin-bottom: 2rem; }
.hero h1 { font-size: 2.6rem; font-weight: 700; letter-spacing: -0.03em;
           margin: 0; color: var(--text); }
.hero p { color: var(--sub); font-size: 1.1rem; margin: .5rem 0 0; }

/* 입력 카드 */
.stTextArea label p { color: var(--sub); font-size: .9rem; font-weight: 500; }
.stTextArea textarea {
  background: var(--card) !important; color: var(--text) !important;
  border: 1px solid var(--line) !important; border-radius: 18px !important;
  padding: 1.1rem 1.2rem !important; font-size: 1.05rem; line-height: 1.6;
  box-shadow: var(--shadow); transition: box-shadow .2s, border-color .2s;
}
.stTextArea textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 4px rgba(0,113,227,.2) !important;
}
.stTextArea [data-baseweb="textarea"], .stTextArea [data-baseweb="base-input"] {
  background: transparent !important; border: none !important;
}

/* pill 버튼 */
.stButton > button {
  width: 100%; border-radius: 999px; border: none;
  background: var(--blue); color: #fff; font-size: 1rem; font-weight: 600;
  padding: .7rem 1rem; transition: background .2s, transform .1s;
}
.stButton > button:hover { background: var(--blue-hover); color: #fff; }
.stButton > button:active { transform: scale(.98); }
.stButton > button:focus-visible { outline: 3px solid rgba(0,113,227,.4); outline-offset: 2px; }

/* 결과 카드 */
.stCodeBlock, [data-testid="stCode"] {
  background: var(--card) !important; border-radius: 18px;
  border: 1px solid var(--line); box-shadow: var(--shadow);
  animation: fadein .4s ease;
}
.stCodeBlock pre, [data-testid="stCode"] pre {
  background: var(--card) !important; color: var(--text) !important;
  padding: 1.2rem !important; font-size: 1.05rem; line-height: 1.7;
  font-family: inherit !important;
}
.stCodeBlock code, [data-testid="stCode"] code { font-family: inherit !important; }
h3 { color: var(--text); font-weight: 600; letter-spacing: -0.02em; margin-top: 1.5rem; }

/* 알림 */
[data-testid="stAlert"] { border-radius: 14px; border: none; box-shadow: var(--shadow); }

@keyframes fadein { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* 모바일: 버튼 세로 정렬 */
@media (max-width: 480px) {
  .block-container { padding-top: 2rem; }
  .hero h1 { font-size: 2rem; }
  [data-testid="stHorizontalBlock"] { flex-direction: column; gap: .6rem; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { width: 100% !important; }
}
</style>
"""

st.set_page_config(page_title="번역기", page_icon="🌐")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><h1>번역기</h1>'
    "<p>글을 입력하고 원하는 언어를 선택하세요.</p></div>",
    unsafe_allow_html=True,
)

text = st.text_area(
    "번역할 텍스트",
    height=200,
    max_chars=MAX_CHARS,
    help=f"최대 {MAX_CHARS:,}자",
    placeholder="여기에 번역할 글을 입력하세요",
)

cols = st.columns(len(LANGUAGES))
clicked = None
for col, label in zip(cols, LANGUAGES):
    if col.button(label, use_container_width=True):
        clicked = label

if clicked:
    if not text.strip():
        st.warning("번역할 텍스트를 입력해주세요.")
    else:
        try:
            with st.spinner(f"{clicked}로 번역 중..."):
                result = translate(text, LANGUAGES[clicked])
            st.subheader(f"번역 결과 ({clicked})")
            st.code(result, language=None, wrap_lines=True)
        except Exception as e:
            st.error(f"번역 중 오류가 발생했습니다: {e}")
