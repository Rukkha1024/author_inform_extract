# 현재 처한 문제 및 해결 방법

## 🔴 주요 이슈

### Issue 1: Chrome/Chromium 브라우저가 설치되어 있지 않음

**상태:** 🔴 차단 (Blocking)
**심각도:** 높음 (High)
**환경:** WSL/Linux 환경

#### 문제 설명

Selenium 기반의 "Show more" 버튼 자동 클릭 기능을 구현했으나, 현재 개발 환경(WSL)에 Chrome/Chromium 브라우저가 설치되어 있지 않습니다.

```bash
$ google-chrome --version
# 출력 없음 (설치되지 않음)

$ chromium-browser --version
# 출력 없음 (설치되지 않음)
```

#### 영향 범위

- ❌ Selenium 모드로 작동할 수 없음
- ❌ "Show more" 버튼 자동 클릭 불가능
- ❌ 특정 논문(예: "Walking shoes and laterally wedged orthoses...") 추출 불가능
- ✅ 기본 모드(Fallback)로는 부분적 작동 가능

#### 현재 동작

```
[기본 모드] Selenium이 없어 페이지네이션 방식으로 논문을 가져옵니다.
주의: 'Show more' 버튼 뒤에 숨겨진 논문은 가져올 수 없습니다.
```

#### 해결 방법

##### 방법 1: Chromium 설치 (권장 - WSL/Linux)

```bash
# Ubuntu/Debian 기반 시스템
sudo apt update
sudo apt install -y chromium-browser

# 또는 Chromium을 snap으로 설치
sudo snap install chromium

# 설치 확인
chromium-browser --version
```

##### 방법 2: Google Chrome 설치

```bash
# 공식 Google Chrome 다운로드 및 설치
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 설치 확인
google-chrome --version
```

##### 방법 3: Windows에서 Python 직접 실행

Windows에는 이미 Chrome이 설치되어 있을 가능성이 높으므로:

```powershell
# PowerShell에서 직접 실행
python extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
```

---

### Issue 2: 실행 방법의 혼동

**상태:** 🟡 해결 가능 (Clarification needed)
**심각도:** 중간 (Medium)

#### 문제 설명

사용자가 `python main.py`를 실행하려고 했으나, 메인 스크립트는 `extract_papers.py`입니다.

#### 현재 상황

```bash
❌ python main.py              # 파일 없음
✅ python extract_papers.py    # 정답
✅ python script/lab.py        # 대안 (테스트 모드)
```

#### 올바른 사용 방법

##### 1. 명령줄 인자로 URL 전달 (권장)

```bash
python3 extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
```

##### 2. 대화형 모드 (URL 대화형 입력)

```bash
python3 extract_papers.py
# 프롬프트: 저자 프로필 URL: [입력 대기]
```

##### 3. 출력 디렉토리 지정

```bash
python3 extract_papers.py "URL" -o my_output_dir
```

##### 4. config.yaml 설정 후 실행 (테스트 모드)

```bash
# config.yaml에서 author_profile_url 수정
python3 script/lab.py
```

---

### Issue 3: 실제 테스트 미실시

**상태:** 🟡 보류 중 (Pending)
**심각도:** 중간 (Medium)

#### 문제 설명

다음과 같은 이유로 실제 테스트를 진행하지 못했습니다:

1. Chrome 미설치로 Selenium 모드 불가능
2. "Show more" 버튼 클릭 기능 미검증
3. 특정 논문 추출 미검증

#### 검증되지 않은 항목

- [ ] Selenium으로 "Show more" 버튼 감지 및 클릭
- [ ] "Show more" 버튼 여러 번 클릭 반복
- [ ] 모든 논문 링크 수집 완료
- [ ] 특정 논문("Walking shoes...") 추출 성공
- [ ] XML 형식 올바른지 확인
- [ ] 파일 저장 성공 여부

#### 필요한 검증

Chrome 설치 후:

```bash
# 1. 전체 시스템 테스트
python3 extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"

# 2. 특정 논문 추출 테스트
python3 test_specific_paper.py

# 3. 논문 목록 확인
python3 quick_list_papers.py

# 4. 생성된 XML 파일 확인
cat output/*.xml | head -100
```

---

### Issue 4: plan.md 목표 달성 검증

**상태:** 🟡 부분 완료 (Partially Done)
**심각도:** 낮음 (Low)

#### 현황

| 목표 | 상태 | 비고 |
|------|------|------|
| 저자 URL 입력 인터페이스 | ✅ 완료 | extract_papers.py 구현 |
| 모든 논문 세부 정보 추출 | ✅ 코드 완료 | 실제 테스트 필요 |
| XML 형식 정리 | ✅ 코드 완료 | 실제 테스트 필요 |
| "Show more" 자동 클릭 | ✅ 코드 완료 | 실제 테스트 필요 |
| 자동화 | ✅ 완료 | Python 스크립트 |
| 새로운 저자 적용 | ✅ 설계 완료 | 실제 테스트 필요 |

#### 검증 체크리스트

- [ ] 저자 프로필 URL로 모든 논문 수집 테스트
- [ ] "Walking shoes and laterally wedged orthoses..." 논문 추출 확인
- [ ] XML 형식 올바른지 검증
- [ ] 다른 저자 프로필로 테스트
- [ ] 논문 수 많은 저자로 테스트 (100개 이상)
- [ ] 에러 처리 테스트 (잘못된 URL, 네트워크 오류 등)

---

## 🟡 부차 이슈

### Issue 5: 페이지네이션 vs Selenium 모드 전환

**상태:** ℹ️ 정보 전달 필요
**심각도:** 낮음 (Low)

#### 현황

사용자가 Selenium 없을 때 자동으로 기본 모드로 전환된다는 것을 명확히 이해하지 못할 수 있습니다.

#### 출력 메시지

```
[Selenium 모드] 'Show more' 버튼을 자동으로 클릭하여 모든 논문을 가져옵니다.
                ↓
[기본 모드] Selenium이 없어 페이지네이션 방식으로 논문을 가져옵니다.
주의: 'Show more' 버튼 뒤에 숨겨진 논문은 가져올 수 없습니다.
```

#### 개선 방법

- 모드 선택 시 명확한 안내 메시지 제공
- 예상되는 논문 수 차이 정보 제공
- Chrome 설치 권장 메시지 표시

---

## 📋 해결 우선순위

### 1순위: Chrome 설치 (필수)

```bash
sudo apt update
sudo apt install -y chromium-browser
```

**소요 시간:** 5-10분

### 2순위: 실제 테스트 실행

Chrome 설치 후:

```bash
# 전체 테스트
python3 extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"

# 특정 논문 확인
python3 test_specific_paper.py
```

**소요 시간:** 10-30분 (저자 논문 수에 따라)

### 3순위: 테스트 결과 검증

생성된 XML 파일 확인:

```bash
# 파일 목록
ls -lh output/*.xml

# 파일 내용 미리보기
head -100 output/*.xml
```

---

## ✅ 완료된 항목

- ✅ Selenium 구현 완료
- ✅ "Show more" 버튼 자동 클릭 코드 작성
- ✅ CLI 인터페이스 완성
- ✅ XML 형식 구현
- ✅ 오류 처리 및 재시도 메커니즘
- ✅ 문서 및 설명서 작성
- ✅ 모듈 의존성 정리

---

## 📌 다음 단계

1. **[긴급]** Chrome/Chromium 설치
   ```bash
   sudo apt install -y chromium-browser
   ```

2. **[필수]** 실제 테스트 실행
   ```bash
   python3 extract_papers.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
   ```

3. **[검증]** 특정 논문 추출 확인
   ```bash
   python3 test_specific_paper.py
   ```

4. **[완료]** 결과 검증 및 Git 커밋

---

## 📞 지원 정보

- **GitHub Issues:** 문제 보고
- **README.md:** 사용 설명서
- **requirements.txt:** 필수 패키지

---

*마지막 업데이트: 2025-10-17*
