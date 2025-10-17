# Google Scholar 논문 정보 추출 도구

Google Scholar 저자 프로필에서 모든 논문 정보를 자동으로 추출하여 XML 형식으로 저장하는 도구입니다.

## 기능

- ✅ 저자 프로필 URL만 입력하면 모든 논문 정보 자동 추출
- ✅ "Show more" 버튼 자동 클릭 (Selenium 사용)
- ✅ 페이지네이션 자동 처리 (모든 논문 수집)
- ✅ 통일된 XML 형식으로 일괄 정리
- ✅ 재시도 메커니즘 (네트워크 오류 대응)
- ✅ 진행 상황 실시간 표시

## 설치

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Chrome 브라우저 설치 (WSL/Linux 환경)

**모든 논문을 추출하려면 Chrome이 필요합니다** (Show more 버튼 클릭을 위해)

#### Ubuntu/Debian (WSL 포함):

```bash
# Chrome 다운로드 및 설치
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 또는 Chromium 설치 (대안)
sudo apt install -y chromium-browser
```

#### Chrome 없이 사용하기:

Chrome이 없어도 기본 모드로 작동하지만, **"Show more" 버튼 뒤에 숨겨진 논문은 가져올 수 없습니다.**

## 사용법

### 방법 1: 명령줄에서 URL 전달

```bash
python3 extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
```

### 방법 2: 대화형 모드

```bash
python3 extract_papers.py
```

프롬프트에서 저자 프로필 URL을 입력하세요.

### 방법 3: config.yaml 설정 후 테스트

```bash
# config.yaml에서 author_profile_url 수정 후
python3 script/lab.py
```

### 방법 4: 출력 디렉토리 지정

```bash
python3 extract_papers.py "URL" -o my_output
```

## 출력 형식

논문 정보는 다음과 같은 XML 형식으로 저장됩니다:

```xml
<?xml version="1.0" ?>
<Articles>
  <Article>
    <Title>논문 제목</Title>
    <Authors>
      <Author>저자1</Author>
      <Author>저자2</Author>
    </Authors>
    <PublicationDate>2024</PublicationDate>
    <Journal>저널명</Journal>
    <Volume>권 번호</Volume>
    <Pages>페이지</Pages>
    <Publisher>출판사</Publisher>
    <Citations>인용 수</Citations>
    <Abstract>초록</Abstract>
    <URL>논문 링크</URL>
  </Article>
  ...
</Articles>
```

## 설정

`config.yaml` 파일에서 다음 설정을 변경할 수 있습니다:

- `author_profile_url`: 기본 저자 프로필 URL
- `user_agent`: HTTP 요청에 사용할 User-Agent
- `output_dir`: 출력 디렉토리
- `retry_count`: 재시도 횟수
- `request_delay`: 요청 간 대기 시간

## 문제 해결

### Chrome 관련 오류

```
selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start
```

**해결책:**
1. Chrome이 설치되어 있는지 확인: `google-chrome --version`
2. WSL 환경에서는 추가 설정 필요:
   ```bash
   export DISPLAY=:0
   ```
3. Chrome 대신 Chromium 사용: `sudo apt install chromium-browser`

### Rate Limiting (429 오류)

Google Scholar에서 요청을 차단하는 경우:
- `config.yaml`에서 `request_delay` 값 증가 (기본: 1초 → 3초 이상)
- 잠시 대기 후 다시 시도

### "Show more" 버튼을 찾을 수 없음

- Selenium이 설치되어 있는지 확인
- Chrome이 정상적으로 실행되는지 확인
- 네트워크 연결 확인

## 시스템 요구사항

- Python 3.7 이상
- Chrome 또는 Chromium 브라우저 (Selenium 모드)
- 인터넷 연결

## 주의사항

- Google Scholar의 이용 약관을 준수하세요
- 과도한 요청은 IP 차단을 유발할 수 있습니다
- `request_delay` 설정을 통해 적절한 대기 시간을 유지하세요

## 라이선스

MIT License

## 문의

문제가 발생하면 GitHub Issues에 등록해주세요.
