import json
import os
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any

from openai import OpenAI

from app.config import settings
from app.models.interview_schemas import (
    AIFeedback,
    AIQuestion,
    Domain,
    FeedbackResponse,
    Level,
    QARecord,
    RoundFeedback,
    ScoreBreakdown,
    SessionExportResponse,
)

# ── 도메인별 핵심 CS 주제 ──────────────────────────────────────────────────────
DOMAIN_TOPICS: Dict[str, list[str]] = {
    Domain.AI: ["머신러닝 기초", "딥러닝 아키텍처", "모델 평가 지표", "데이터 전처리", "최적화 알고리즘", "과적합/정규화"],
    Domain.BACKEND: ["데이터베이스 & 트랜잭션", "운영체제 & 프로세스", "네트워크 & HTTP", "시스템 설계", "API 설계", "캐싱 전략"],
    Domain.FRONTEND: ["브라우저 렌더링", "JavaScript 이벤트 루프", "성능 최적화", "상태 관리", "CSS & 레이아웃", "웹 보안"],
}

# ── 숙련도별 질문 스타일 안내 ──────────────────────────────────────────────────
LEVEL_GUIDE: Dict[str, str] = {
    Level.NEW: "기본 개념과 정의 위주로, 실무 경험이 없는 신입생에게 묻는 수준으로 출제하라.",
    Level.JUNIOR: "개념 이해와 간단한 적용 사례를 함께 묻는 주니어(1~3년) 수준으로 출제하라.",
    Level.SENIOR: "설계 결정, 트레이드오프, 장애 대응 경험을 묻는 시니어(5년 이상) 수준으로 출제하라.",
}

# ── 세션 저장 경로 ─────────────────────────────────────────────────────────────
SESSION_DIR = "interview_sessions"

# ── Few-shot 예시 파일 경로 ────────────────────────────────────────────────────
FEW_SHOT_PATH = os.path.join(os.path.dirname(__file__), "../../data/few_shot_examples.json")


class InterviewService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # 인메모리 세션 저장소: session_id → dict
        self._sessions: Dict[str, dict] = {}
        os.makedirs(SESSION_DIR, exist_ok=True)
        # Few-shot 예시 로드
        self._few_shot: Dict[str, Any] = self._load_few_shot()

    def _load_few_shot(self) -> List[Dict[str, Any]]:
        """서비스 시작 시 공통 few-shot 예시 JSON을 한 번만 로드"""
        path = os.path.normpath(FEW_SHOT_PATH)
        if not os.path.exists(path):
            print(f"[Warning] few-shot 파일을 찾을 수 없습니다: {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_few_shot_messages(self) -> List[Dict[str, str]]:
        """
        공통 few-shot 예시를 user/assistant 메시지 쌍으로 반환.
        첫 번째 user 메시지에 '이하 예시를 반드시 따르라'는 앵커를 추가해
        모델이 형식과 스타일을 강하게 학습하도록 한다.
        """
        if not self._few_shot:
            return []

        messages: List[Dict[str, str]] = []
        # 첫 쌍에만 앵커 프리픽스를 붙여 few-shot 전체의 중요도를 높임
        for i, ex in enumerate(self._few_shot):
            prefix = (
                "[필수 참고 예시] 아래 예시들의 topic·question 형식과 질문 수준을 반드시 따라야 한다.\n"
                if i == 0 else ""
            )
            messages.append({"role": "user", "content": prefix + ex["user"]})
            messages.append({"role": "assistant", "content": json.dumps(ex["assistant"], ensure_ascii=False)})
        return messages

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────────────

    def _save_session(self, session_id: str) -> None:
        """세션을 JSON 파일로 즉시 저장 (기능 03 – 유실 방지)"""
        session = self._sessions[session_id]
        path = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)

    def _load_session(self, session_id: str) -> Optional[dict]:
        """인메모리에 없으면 파일에서 복구"""
        if session_id in self._sessions:
            return self._sessions[session_id]
        path = os.path.join(SESSION_DIR, f"{session_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                session = json.load(f)
            self._sessions[session_id] = session
            return session
        return None

    def _build_persona_prompt(self, level: str, domain: str) -> str:
        """기능 01 – AI 페르소나 시스템 프롬프트 생성"""
        domain_label = {Domain.AI: "AI/ML", Domain.BACKEND: "백엔드", Domain.FRONTEND: "프론트엔드"}.get(domain, domain)
        level_label = {Level.NEW: "신입", Level.JUNIOR: "주니어", Level.SENIOR: "시니어"}.get(level, level)
        return (
            f"너는 10년 차 {domain_label} 시니어 면접관이야. "
            f"지금 {level_label} 지원자를 면접하고 있어. "
            f"{LEVEL_GUIDE.get(level, '')} "
            "질문은 반드시 JSON 형식으로만 반환해야 해."
        )

    def _generate_question(self, session: dict) -> AIQuestion:
        """기능 02 – OpenAI로 도메인 특화 질문 생성 (response_format=json_object)"""
        history = session["interview_history"]
        used_topics = [r["topic"] for r in history]
        topics = DOMAIN_TOPICS.get(session["domain"], [])
        # 아직 사용하지 않은 주제 우선 선택
        remaining = [t for t in topics if t not in used_topics]
        priority_hint = f"이번엔 '{remaining[0]}' 주제로 질문해줘." if remaining else "앞서 다루지 않은 새 주제로 질문해줘."

        few_shot = self._build_few_shot_messages()

        messages = [
            {"role": "system", "content": self._build_persona_prompt(session["level"], session["domain"])},
            *few_shot,  # 도메인·숙련도별 예시 삽입
            {
                "role": "user",
                "content": (
                    f"{priority_hint} "
                    "위 예시들과 동일한 질문 스타일·깊이를 유지하면서 새로운 질문을 만들어줘. "
                    "응답은 반드시 아래 JSON 스키마만 출력해야 해:\n"
                    '{"topic": "<출제 주제>", "question": "<면접 질문 전문>"}'
                ),
            },
        ]

        response = self.client.chat.completions.create(
            model=settings.INTERVIEW_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5,  # few-shot 일관성을 위해 낮춤
        )

        raw = json.loads(response.choices[0].message.content)
        return AIQuestion(topic=raw["topic"], question=raw["question"])

    # ── 피드백 평가 기준 (프롬프트 상수) ──────────────────────────────────────────
    _SCORING_RUBRIC = """
## 평가 기준 (총 100점) — 반드시 아래 기준을 엄격히 적용하라

### 1. 논리적 답변 구조 (20점)
- 18~20점: 두괄식(결론→근거→사례) 또는 STAR 기법이 완벽히 적용됨. 흐름이 자연스럽고 논리적 비약 없음.
- 13~17점: 구조가 있으나 일부 산만하거나 결론이 후반부에 등장함.
- 7~12점: 나열식 답변. 논리적 연결 없이 키워드만 나열.
- 0~6점: 질문과 맞지 않거나 두서없는 답변.

### 2. 기술적 정확성 (25점)
- 22~25점: 모든 개념·용어·원리가 정확함. 오개념 전무.
- 16~21점: 핵심 개념은 정확하나 세부 설명에 사소한 오류.
- 9~15점: 중요 개념에 오류가 있거나 불완전한 설명.
- 0~8점: 핵심 개념을 잘못 이해하거나 전혀 모름.

### 3. 구체성·사례 제시 (20점)
- 18~20점: 실제 수치, 구체적 경험, 코드/설계 사례 등을 명확히 제시.
- 13~17점: 일부 구체적 사례가 있으나 추상적 표현과 혼재.
- 7~12점: 대부분 추상적 표현("잘 한다", "효율적이다" 등).
- 0~6점: 구체성이 전혀 없음.

### 4. 전달력·명확성 (15점)
- 13~15점: 핵심만 간결하게 전달. 불필요한 중복 없음.
- 9~12점: 대체로 명확하나 일부 장황하거나 핵심이 묻힘.
- 5~8점: 장황하거나 핵심 전달이 불명확.
- 0~4점: 의미 파악이 어려울 정도로 불명확.

### 5. 지식의 깊이 (20점)
- 18~20점: 정의를 넘어 원리, 장단점, 트레이드오프까지 설명. 연관 개념 언급.
- 13~17점: 개념 이해에 깊이가 있으나 트레이드오프 설명 부족.
- 7~12점: 교과서 수준의 정의 암기에 머무름.
- 0~6점: 개념의 표면적 용어만 언급.

## 보수적 채점 원칙 — 반드시 준수
- 실제 채용 면접 기준을 적용한다. 관대하게 점수를 주지 않는다.
- 전체 지원자의 점수 분포 기준: 하위 30%는 50점 미만, 중위 40%는 50~69점, 상위 20%는 70~84점, 상위 5%만 85점 이상.
- 80점 이상은 "명확한 근거"가 있을 때만 부여한다.
- 답변이 짧거나 모호하면 구체성·깊이 항목에서 가차없이 감점한다.
- score_breakdown의 각 항목 합산이 반드시 total_score와 일치해야 한다.
"""

    def _generate_feedback(self, session: dict) -> AIFeedback:
        """기능 04 – 5개 평가 항목 기반 상세 피드백 생성 (보수적 채점)"""
        history_text = "\n\n".join(
            f"[Round {r['round']}] 주제: {r['topic']}\n"
            f"질문: {r['question']}\n"
            f"답변: {r['answer']}"
            for r in session["interview_history"]
        )

        level_label = {Level.NEW: "신입", Level.JUNIOR: "주니어", Level.SENIOR: "시니어"}.get(
            session["level"], session["level"]
        )

        schema = (
            "{\n"
            '  "total_score": <score_breakdown 5개 합산, 정수>,\n'
            '  "score_breakdown": {\n'
            '    "logical_structure": <0~20 정수>,\n'
            '    "technical_accuracy": <0~25 정수>,\n'
            '    "concreteness": <0~20 정수>,\n'
            '    "communication": <0~15 정수>,\n'
            '    "depth": <0~20 정수>\n'
            '  },\n'
            '  "per_round_feedback": [\n'
            '    {"round": 1, "comment": "<이 라운드 답변의 핵심 문제점 또는 잘한 점 1~2문장>"},\n'
            '    ...\n'
            '  ],\n'
            '  "strengths": "<전체 답변에서 두드러진 강점을 구체적 근거와 함께 3~5문장으로>",\n'
            '  "weaknesses": "<보완이 필요한 약점을 구체적 근거와 함께 3~5문장으로>",\n'
            '  "recommended_keywords": ["<공부 키워드1>", "<키워드2>", "<키워드3>", ...]\n'
            "}"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    self._build_persona_prompt(session["level"], session["domain"]) + "\n\n"
                    + self._SCORING_RUBRIC
                ),
            },
            {
                "role": "user",
                "content": (
                    f"아래는 {level_label} 지원자의 전체 면접 문답 기록이야. "
                    "위 평가 기준과 보수적 채점 원칙을 반드시 적용하여 종합 평가해줘. "
                    "각 라운드 답변도 개별적으로 코멘트해야 해.\n\n"
                    f"{history_text}\n\n"
                    f"응답은 반드시 아래 JSON 스키마만 출력해야 해:\n{schema}"
                ),
            },
        ]

        response = self.client.chat.completions.create(
            model=settings.INTERVIEW_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,  # 채점 일관성을 위해 낮게 설정
        )

        raw = json.loads(response.choices[0].message.content)
        bd = raw["score_breakdown"]

        return AIFeedback(
            total_score=raw["total_score"],
            score_breakdown=ScoreBreakdown(
                logical_structure=bd["logical_structure"],
                technical_accuracy=bd["technical_accuracy"],
                concreteness=bd["concreteness"],
                communication=bd["communication"],
                depth=bd["depth"],
            ),
            per_round_feedback=[
                RoundFeedback(round=r["round"], comment=r["comment"])
                for r in raw["per_round_feedback"]
            ],
            strengths=raw["strengths"],
            weaknesses=raw["weaknesses"],
            recommended_keywords=raw["recommended_keywords"],
        )

    def _build_feedback_response(self, session_id: str, user_name: str, fb: dict) -> FeedbackResponse:
        """저장된 피드백 dict → FeedbackResponse 변환 (중복 제거용 헬퍼)"""
        bd = fb["score_breakdown"]
        return FeedbackResponse(
            session_id=session_id,
            user_name=user_name,
            total_score=fb["total_score"],
            score_breakdown=ScoreBreakdown(
                logical_structure=bd["logical_structure"],
                technical_accuracy=bd["technical_accuracy"],
                concreteness=bd["concreteness"],
                communication=bd["communication"],
                depth=bd["depth"],
            ),
            per_round_feedback=[
                RoundFeedback(round=r["round"], comment=r["comment"])
                for r in fb["per_round_feedback"]
            ],
            strengths=fb["strengths"],
            weaknesses=fb["weaknesses"],
            recommended_keywords=fb["recommended_keywords"],
        )

    # ── 공개 API ──────────────────────────────────────────────────────────────

    def init_session(self, name: str, level: str, domain: str, total_rounds: int) -> dict:
        """기능 01 – 세션 초기화 및 첫 질문 생성"""
        session_id = str(uuid.uuid4())

        session = {
            "session_id": session_id,
            "user_name": name,
            "level": level,
            "domain": domain,
            "total_rounds": total_rounds,
            "current_round": 1,
            "interview_history": [],
            "feedback": None,
            "created_at": datetime.utcnow().isoformat(),
            "is_complete": False,
        }
        self._sessions[session_id] = session

        # 첫 질문 생성
        first_q = self._generate_question(session)
        session["pending_question"] = {"topic": first_q.topic, "question": first_q.question}
        self._save_session(session_id)

        return {
            "session_id": session_id,
            "first_question": first_q.question,
            "current_round": 1,
            "total_rounds": total_rounds,
        }

    def submit_answer(self, session_id: str, answer: str) -> dict:
        """기능 02/03 – 답변 저장 후 다음 질문 또는 완료 처리"""
        session = self._load_session(session_id)
        if session is None:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        if session["is_complete"]:
            raise ValueError("이미 종료된 면접 세션입니다.")

        pending = session.get("pending_question")
        if not pending:
            raise ValueError("현재 라운드에 질문이 없습니다.")

        # 기능 03 – 문답 기록 저장
        record = QARecord(
            round=session["current_round"],
            topic=pending["topic"],
            question=pending["question"],
            answer=answer,
        )
        session["interview_history"].append(record.model_dump())

        completed_round = session["current_round"]

        if completed_round >= session["total_rounds"]:
            # 모든 라운드 완료
            session["is_complete"] = True
            session["pending_question"] = None
            self._save_session(session_id)
            return {
                "round_completed": completed_round,
                "next_question": None,
                "current_round": None,
                "is_complete": True,
            }
        else:
            # 다음 라운드 진행
            session["current_round"] += 1
            next_q = self._generate_question(session)
            session["pending_question"] = {"topic": next_q.topic, "question": next_q.question}
            self._save_session(session_id)
            return {
                "round_completed": completed_round,
                "next_question": next_q.question,
                "current_round": session["current_round"],
                "is_complete": False,
            }

    def get_feedback(self, session_id: str) -> FeedbackResponse:
        """기능 04 – 종합 피드백 생성 (완료된 세션에서만 호출 가능)"""
        session = self._load_session(session_id)
        if session is None:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
        if not session["is_complete"]:
            raise ValueError("면접이 아직 진행 중입니다. 모든 라운드를 완료한 후 호출하세요.")

        # 이미 생성된 피드백이 있으면 재사용
        if session.get("feedback"):
            fb = session["feedback"]
            return self._build_feedback_response(session_id, session["user_name"], fb)

        ai_fb = self._generate_feedback(session)
        session["feedback"] = ai_fb.model_dump()
        self._save_session(session_id)

        return self._build_feedback_response(session_id, session["user_name"], session["feedback"])

    def export_session(self, session_id: str) -> SessionExportResponse:
        """기능 05 – 전체 세션 데이터 반환 및 파일 저장"""
        session = self._load_session(session_id)
        if session is None:
            raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")

        # 파일은 항상 최신 상태로 덮어쓰기
        self._save_session(session_id)

        feedback = None
        if session.get("feedback"):
            feedback = self._build_feedback_response(
                session_id, session["user_name"], session["feedback"]
            )

        return SessionExportResponse(
            session_id=session_id,
            user_name=session["user_name"],
            level=session["level"],
            domain=session["domain"],
            total_rounds=session["total_rounds"],
            interview_history=[QARecord(**r) for r in session["interview_history"]],
            feedback=feedback,
        )


interview_service = InterviewService()
