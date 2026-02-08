# Hhugginface 음성 데이터
# Window는 Decoding을 위해 ffmeg 별도 설치 필요
# pip install --upgrade --force-reinstall torch torchaudio --index-url https://download.pytorch.org/whl/cpu
# pip install --upgrade datasets torchcodec

from datasets import load_dataset

# Load Zeroth-Korean dataset
# dataset = load_dataset("kresnik/zeroth_korean")

# 데이터 불러오기
def get_korean_dataset():
    dataset = load_dataset("kresnik/zeroth_korean", split="train")
    return dataset


# Print an example from the training dataset
# print(dataset['train'][0])
