import hashlib
import re
from datetime import datetime

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="T1 퀴즈 챌린지",
    page_icon="🏆",
    layout="wide",
)


USERS = {
    "faker": hashlib.sha256("mid".encode()).hexdigest(),
    "doran": hashlib.sha256("top".encode()).hexdigest(),
    "keria": hashlib.sha256("sup".encode()).hexdigest(),
}


@st.cache_data(show_spinner=False)
def load_quiz_data() -> list[dict]:
    return [
        {
            "type": "mcq",
            "question": "Faker의 본명은?",
            "options": ["이상혁", "류민석", "문현준", "최현준"],
            "answer": "이상혁",
            "explanation": "류민석 선수는 Keria, 문현준 선수는 Oner, 최현준 선수는 Doran이라는 이름으로 활동 중입니다.",
        },
        {
            "type": "short",
            "question": "T1은 월즈에서 총 몇 번 우승했나요?",
            "answer": "6",
            "explanation": "T1은 2013, 2015, 2016, 2023, 2024, 2025년에 월즈 우승을 차지했습니다.",
        },
        {
            "type": "short",
            "question": "현 T1의 주장의 이름을 영어로 입력하세요. (소문자)",
            "answer": "faker",
            "explanation": "faker 이상혁 선수는 2017년부터 현재까지 T1의 주장을 맡고 있습니다.",
        },
        {
            "type": "mcq",
            "question": "T1에 대한 사실이 아닌 것을 고르세요.",
            "options": [
                "1. T1은 월즈에서 최초이자 유일하게 쓰리핏을 달성했다.",
                "2. T1은 항상 4시드로 월즈에 진출해 우승했다.",
                "3. T1은 동일 로스터로 3연속 결승에 진출했다.",
                "4. T1은 월즈 결승에 8번 진출했으며, 이는 최다 기록이다.",
            ],
            "answer": "2. T1은 항상 4시드로 월즈에 진출해 우승했다.",
            "explanation": "T1은 여러 시드(1,2,3,4 시드) 자격으로 월즈 우승을 했습니다.",
        },
        {
            "type": "ox",
            "question": "T1의 마스코트는 불사조이다.",
            "answer": "O",
            "explanation": "T1의 마스코트는 불사조이며, 이름은 Ati입니다.",
        },
    ]


@st.cache_data(show_spinner=False)
def build_score_frame(records: tuple[tuple[str, int, str], ...]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=["사용자", "점수", "제출 시각"])
    return pd.DataFrame(records, columns=["사용자", "점수", "제출 시각"])


def init_session_state() -> None:
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("latest_score", 0)
    st.session_state.setdefault("score_history_by_user", {})


def login_panel() -> None:
    st.subheader("로그인")
    st.caption("데모 계정: faker / mid")
    st.caption("데모 계정: doran / top")
    st.caption("데모 계정: keria / sup")

    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", use_container_width=True)

    if submitted:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if USERS.get(username) == hashed:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"{username}님, 환영합니다.")
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")


def logout_button() -> None:
    if st.button("로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.quiz_submitted = False
        st.session_state.latest_score = 0
        st.rerun()


def get_fan_type(score: int) -> str:
    if score == 100:
        return "하드코어 T1 팬"
    if score >= 60:
        return "일반 팬"
    return "라이트 팬"


def get_current_user_history() -> list[tuple[str, int, str]]:
    username = st.session_state.username
    return st.session_state.score_history_by_user.get(username, [])


def get_all_history() -> list[tuple[str, int, str]]:
    all_records: list[tuple[str, int, str]] = []
    for user_records in st.session_state.score_history_by_user.values():
        all_records.extend(user_records)
    return all_records


def normalize_answer(text: str) -> str:
    cleaned = text.strip().lower()
    numbers = re.findall(r"\d+", cleaned)
    if numbers:
        return numbers[0]
    return cleaned


def hero_section() -> None:
    st.title("🏆 Streamlit을 이용한 T1 퀴즈")
    st.write("학번: 2024404039")
    st.write("이름: 오기민")
    st.write("리그 오브 레전드 프로게임단 T1을 주제로 한 퀴즈입니다.")
    st.caption("로그인 후 문제를 풀고, 내 기록과 팬 유형을 확인해보세요.")


def render_sidebar() -> None:
    with st.sidebar:
        st.header("앱 정보")
        st.write("`streamlit` 중간고사 대체 과제용 예시 앱입니다.")
        st.write(f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if st.session_state.logged_in:
            st.success(f"접속 중: {st.session_state.username}")
            logout_button()


def quiz_section() -> None:
    with st.spinner("퀴즈 데이터를 불러오는 중..."):
        questions = load_quiz_data()

    st.subheader("퀴즈 풀기")

    with st.form("quiz_form"):
        answers = []
        for idx, item in enumerate(questions, start=1):
            if item["type"] == "mcq":
                answer = st.radio(
                    f"{idx}. {item['question']}",
                    item["options"],
                    key=f"q_{idx}",
                )
            elif item["type"] == "ox":
                answer = st.radio(
                    f"{idx}. {item['question']}",
                    ["O", "X"],
                    key=f"q_{idx}",
                )
            else:
                answer = st.text_input(
                    f"{idx}. {item['question']}",
                    key=f"q_{idx}",
                )
            answers.append(answer)

        submitted = st.form_submit_button("제출하기", use_container_width=True)

    if submitted:
        score = 0
        for user_answer, item in zip(answers, questions):
            if item["type"] == "short":
                is_correct = normalize_answer(user_answer) == normalize_answer(item["answer"])
            else:
                is_correct = user_answer == item["answer"]

            if is_correct:
                score += 20

        st.session_state.quiz_submitted = True
        st.session_state.latest_score = score
        username = st.session_state.username
        user_history = st.session_state.score_history_by_user.setdefault(username, [])
        user_history.append(
            (
                username,
                score,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        st.rerun()

    if st.session_state.quiz_submitted:
        score = st.session_state.latest_score
        st.metric("최근 점수", f"{score}점")
        st.success(f"당신의 유형: {get_fan_type(score)}")
        for idx, item in enumerate(questions, start=1):
            with st.expander(f"{idx}번 문제 정답 보기"):
                st.write(f"정답: **{item['answer']}**")
                st.caption(item["explanation"])
        if score == 100:
            st.balloons()


def stats_section() -> None:
    st.subheader("기록 보기")

    user_records = tuple(tuple(row) for row in get_current_user_history())
    all_records = tuple(tuple(row) for row in get_all_history())

    user_df = build_score_frame(user_records)
    all_df = build_score_frame(all_records)

    st.markdown("**내 기록**")
    if user_df.empty:
        st.info("현재 로그인한 사용자의 제출 기록이 아직 없습니다.")
    else:
        top_left, top_right = st.columns([1, 1])
        with top_left:
            st.dataframe(
                user_df.sort_values("제출 시각", ascending=False),
                use_container_width=True,
            )
        with top_right:
            st.metric("내 최고 점수", f"{user_df['점수'].max()}점")
            st.metric("내 평균 점수", f"{user_df['점수'].mean():.1f}점")
            st.metric("내 응시 횟수", int(user_df.shape[0]))

    st.markdown("**전체 랭킹**")
    if all_df.empty:
        st.info("아직 아무도 퀴즈를 제출하지 않았습니다.")
        return

    ranking_df = (
        all_df.groupby("사용자", as_index=False)
        .agg(
            최고점수=("점수", "max"),
            평균점수=("점수", "mean"),
            응시횟수=("점수", "count"),
        )
        .sort_values(["최고점수", "평균점수", "응시횟수"], ascending=[False, False, False])
        .reset_index(drop=True)
    )
    ranking_df.index = ranking_df.index + 1

    bottom_left, bottom_right = st.columns([1, 1])
    with bottom_left:
        st.dataframe(ranking_df, use_container_width=True)
    with bottom_right:
        st.metric("전체 최고 점수", f"{all_df['점수'].max()}점")
        st.metric("전체 평균 점수", f"{all_df['점수'].mean():.1f}점")
        st.metric("전체 제출 수", int(all_df.shape[0]))


def main() -> None:
    init_session_state()
    render_sidebar()
    hero_section()

    if not st.session_state.logged_in:
        login_panel()
        st.info("로그인하면 퀴즈와 기록 기능이 열립니다.")
        return

    left, right = st.columns([1.2, 0.8])
    with left:
        quiz_section()
    with right:
        stats_section()


if __name__ == "__main__":
    main()
