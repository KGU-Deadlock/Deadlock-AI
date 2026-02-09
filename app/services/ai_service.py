import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
# .env 파일에 저장된 키를 불러옵니다.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIService:
    def __init__(self):
        # 대장이 설계한 시니어 개발자 페르소나를 여기에 주입합니다!
        self.system_instruction = """
        너는 'HelloCS'의 시니어 개발자 면접관이야. 
        사용자의 답변을 분석해서 반드시 JSON 형식으로만 응답해줘.
        틀린 부분은 <highlight> 태그로 감싸는 거 잊지 말고!
        """
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=self.system_instruction
        )

    async def get_feedback(self, question, user_answer, model_answer=None):
        prompt = f"질문: {question}\n사용자 답변: {user_answer}\n참고 답안: {model_answer}"
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text
