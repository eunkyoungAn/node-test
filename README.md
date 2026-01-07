# Career Todo (커리어캐쳐 스타일)

간단한 콘솔 기반 Todo 앱입니다. 비개발자도 쉽게 실행할 수 있도록
데이터는 사용자 홈 폴더의 `.career_todo/todos.json`에 저장됩니다.

## 요구사항
- Python 3.8 이상 (스크립트 실행 시)
- Windows (EXE/인스톨러용)

## 실행 방법

### 1. Python 스크립트 실행
터미널에서:
```bash
python career_todo.py
```

### 2. 웹 버전 실행 (브라우저)
Flask 설치 후:
```bash
pip install flask
python app.py
```
브라우저에서 http://127.0.0.1:5000/ 열기

### 3. Windows EXE 실행
빌드된 EXE 파일:
```bash
.\dist_icon\CareerTodoIcon.exe
```
더블클릭으로 실행 가능.

### 4. 배치 파일 실행
Windows에서 더블클릭:
```bash
run_career_todo.bat
```

### 5. 인스톨러 설치
인스톨러 실행:
```bash
installer\career_todo_installer.exe
```
설치 후 시작 메뉴/바탕화면 바로가기 생성.

## 데이터 파일 위치
- `{사용자 홈}/.career_todo/todos.json`

## 기능
- Todo 추가/조회/수정/삭제
- 완료 처리 및 미완료 되돌리기
- 필터: 전체/미완료/완료/오늘 마감/이번 주 마감/카테고리별
- 진행률 보기
- 샘플 Todo 자동 생성

## 기타
- 별도 의존성 없음(표준 라이브러리만 사용)
- GitHub: https://github.com/eunkyoungAn/node-test