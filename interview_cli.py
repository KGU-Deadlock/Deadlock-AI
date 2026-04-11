"""
면접 시뮬레이터 커맨드라인 테스트 스크립트

사용법:
    python interview_cli.py

흐름:
    1. 이름 / 숙련도 / 도메인 / 라운드 수 입력
    2. AI 질문 → 사용자 답변 반복
    3. 종합 피드백 출력
    4. JSON 파일 저장 (interview_sessions/<session_id>.json)
"""

import json
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from app.models.interview_schemas import Domain, Level
from app.services.interview_service import interview_service

# ── 터미널 색상 코드 ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def print_divider(char: str = "─", width: int = 60) -> None:
    print(c(char * width, CYAN))


def prompt_choice(label: str, choices: list[str]) -> str:
    """선택지를 출력하고 유효한 입력을 받을 때까지 반복"""
    while True:
        print(c(f"\n[선택] {label}", BOLD))
        for i, choice in enumerate(choices, 1):
            print(f"  {c(str(i), YELLOW)}. {choice}")
        raw = input(c("  >> ", CYAN)).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        print(c("  올바른 번호를 입력하세요.", RED))


def prompt_int(label: str, min_val: int = 1, max_val: int = 10) -> int:
    """정수 범위 입력"""
    while True:
        raw = input(c(f"\n[입력] {label} ({min_val}~{max_val}): ", CYAN)).strip()
        if raw.isdigit() and min_val <= int(raw) <= max_val:
            return int(raw)
        print(c(f"  {min_val}~{max_val} 사이의 숫자를 입력하세요.", RED))


def prompt_text(label: str) -> str:
    """빈 문자열 없이 텍스트 입력"""
    while True:
        raw = input(c(f"\n[입력] {label}: ", CYAN)).strip()
        if raw:
            return raw
        print(c("  값을 입력하세요.", RED))


# ── 메인 흐름 ─────────────────────────────────────────────────────────────────

def run():
    print_divider("═")
    print(c("  Deadlock AI — 면접 시뮬레이터 (CLI)", BOLD + CYAN))
    print_divider("═")

    # ── 1단계: 기본 정보 입력 ────────────────────────────────────────────────
    print(c("\n[ 1단계 ] 기본 정보 입력", BOLD))

    name = prompt_text("이름(ID)")

    level_str = prompt_choice("숙련도", [l.value for l in Level])
    level = Level(level_str)

    domain_str = prompt_choice("도메인", [d.value for d in Domain])
    domain = Domain(domain_str)

    total_rounds = prompt_int("총 라운드 수", min_val=1, max_val=10)

    # ── 2단계: 세션 초기화 ───────────────────────────────────────────────────
    print(c("\n  AI 질문을 생성하는 중...", YELLOW))
    result = interview_service.init_session(
        name=name,
        level=level,
        domain=domain,
        total_rounds=total_rounds,
    )

    session_id = result["session_id"]

    print_divider()
    print(c(f"  세션 ID : {session_id}", BLUE))
    print(c(f"  대상    : {name} / {level.value} / {domain.value} / {total_rounds}라운드", BLUE))
    print_divider()

    # ── 3단계: 라운드 진행 ───────────────────────────────────────────────────
    current_question = result["first_question"]
    current_round = 1

    while True:
        print(c(f"\n[ Round {current_round} / {total_rounds} ]", BOLD + GREEN))
        print_divider("─", 40)
        print(c("Q. ", YELLOW) + current_question)
        print_divider("─", 40)

        answer = prompt_text("내 답변")

        print(c("\n  다음 라운드 준비 중...", YELLOW))
        result = interview_service.submit_answer(session_id=session_id, answer=answer)

        if result["is_complete"]:
            print(c("\n  모든 라운드가 완료되었습니다!", BOLD + GREEN))
            break

        current_question = result["next_question"]
        current_round = result["current_round"]

    # ── 4단계: 종합 피드백 ───────────────────────────────────────────────────
    print(c("\n[ 4단계 ] 종합 피드백 생성 중...", YELLOW))
    feedback = interview_service.get_feedback(session_id)

    print_divider("═")
    print(c("  종합 피드백 리포트", BOLD + CYAN))
    print_divider("═")
    print(c(f"  종합 점수   : {feedback.total_score} / 100", BOLD))
    print()

    # 항목별 세부 점수
    bd = feedback.score_breakdown
    print(c("  [항목별 점수]", BOLD))
    print(f"    논리적 구조   : {bd.logical_structure:>2} / 20")
    print(f"    기술적 정확성 : {bd.technical_accuracy:>2} / 25")
    print(f"    구체성·사례   : {bd.concreteness:>2} / 20")
    print(f"    전달력·명확성 : {bd.communication:>2} / 15")
    print(f"    지식의 깊이   : {bd.depth:>2} / 20")
    print()

    # 라운드별 코멘트
    print(c("  [라운드별 코멘트]", BOLD))
    for rf in feedback.per_round_feedback:
        print(f"    Round {rf.round}: {rf.comment}")
    print()

    print(c("  [강점]", GREEN + BOLD))
    print(f"  {feedback.strengths}")
    print()
    print(c("  [약점]", RED + BOLD))
    print(f"  {feedback.weaknesses}")
    print()
    print(c("  [추천 학습 키워드]", YELLOW + BOLD))
    for kw in feedback.recommended_keywords:
        print(f"    • {kw}")
    print_divider("═")

    # ── 5단계: JSON 파일 출력 ────────────────────────────────────────────────
    export = interview_service.export_session(session_id)
    file_path = f"interview_sessions/{session_id}.json"
    print(c(f"\n  JSON 저장 완료 → {file_path}", BLUE))
    print(c("  interview_sessions/ 디렉토리에서 확인하세요.", BLUE))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(c("\n\n  면접을 중단했습니다. 이전 기록은 interview_sessions/ 에 저장되어 있습니다.", YELLOW))
        sys.exit(0)
    except Exception as e:
        print(c(f"\n  오류 발생: {e}", RED))
        sys.exit(1)
