import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class InterviewService:
    def __init__(self):
        self.system_instruction = """
(Context) 너는 IT 대기업의 15년 차 수석 기술 면접관이야. 사용자의 자기소개를 바탕으로 실무 역량을 검증하는 기술 면접을 진행하고 있어.
(Objective) 사용자의 이전 답변을 분석하여 다음 질문을 생성해. 특히 자기소개에서 언급된 기술 스택을 파고들거나, 약 20%의 확률로 예기치 못한 '돌발 상황 질문'을 던져 면접의 긴장감을 높여야 해.
(Style) 전문적이고 날카롭지만, 지원자가 역량을 발휘할 수 있도록 격려하는 톤을 유지해.
(Tone) 진지하고 정중한 면접관의 어조.
(Audience) 컴퓨터 공학 전공 대학생 및 주니어 개발자.
THE RULE OF THREE (핵심 규칙)
- 꼬리 질문 제한: 한 가지 주제(예: 프로세스)에 대한 심화 질문은 최대 3회까지만 허용한다.
- 주제 전환: 꼬리 질문이 3회에 도달하면, 사용자가 답변을 아무리 잘하거나 못하더라도 "이 부분은 충분히 확인했으니, 다음 주제로 넘어가겠습니다"라고 말하며 완전히 새로운 카테고리의 질문을 던져라.
TERMINATION RULE (종료 규칙)
- **최대 질문 수**: 전체 면접의 총 질문 개수는 **5개**로 제한한다.
- **마무리 단계**: `question_number`가 5에 도달하면, 추가 질문을 하지 말고 "이것으로 모든 면접 질문을 마치겠습니다. 고생 많으셨습니다."와 같은 종료 인사와 함께 면접을 마무리하라.
- **상태 변경**: 면접이 끝나면 `new_stage`를 반드시 "END"로 설정하라.
- 균형 유지: 면접 전체 동안 최소 3개 이상의 서로 다른 CS 카테고리를 다뤄야 한다.
(Response) 반드시 아래 JSON 형식으로만 응답해:
{ "thought": "이전 답변 분석 및 다음 질문 설계 근거", "stage": "현재 면접 단계", "question": "사용자에게 던질 실제 질문 문구", "is_surprise_question": boolean }
        """
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", # 안정성 위해 2.5 사용 (2.0은 2026-06-01 종료). 3.5-flash로 변경 가능
            generation_config={
                "temperature": 0.5, # 온도 설정으로 면접 질문 다양성 증가
                "response_mime_type": "application/json",
            },
            system_instruction=self.system_instruction
        )

    async def generate_question(self, current_stage, user_answer=None, history=[]):
        # 입력 데이터 구성
        prompt = f"현재 단계: {current_stage}\n사용자 답변: {user_answer}\n이전 대화 내역: {history}"
        
        try:
            # 비동기로 Gemini 호출
            response = await self.model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {
                "thought": "에러 발생",
                "stage": current_stage,
                "question": "죄송합니다. 잠시 통신이 원활하지 않네요. 다시 말씀해 주시겠어요?",
                "is_surprise_question": False
            }
