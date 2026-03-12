import torch
from test_stt import load_dataset
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
# test_stt.py에서 get_korean_dataset 함수 임포트
from test_stt import get_korean_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = get_korean_dataset()

result = pipe(dataset[0]["audio"])
print(result["text"])
