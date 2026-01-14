# python version
Python 3.12

# uv sync로 가상환경 생성 및 의존성 자동 설치
uv sync

# 가상환경 활성화
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# 서버 실행
uvicorn src.main:app --reload

# VSCode 디버깅
VSCode를 사용하는 경우, .vscode/launch.json 설정이 포함