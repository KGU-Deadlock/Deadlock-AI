import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert "version" in response.json()


def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_stt_health_check():
    """STT 헬스 체크 테스트"""
    response = client.get("/api/stt/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "model" in response.json()


def test_transcribe_no_file():
    """파일 없이 STT 요청 시 에러 테스트"""
    response = client.post("/api/stt/transcribe")
    assert response.status_code == 422  # Validation error
