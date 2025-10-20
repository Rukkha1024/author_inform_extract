# Google Scholar 저자 스크레이퍼 (Korean README)

이 저장소는 **Google Scholar 저자 프로필**에서 저자 메타데이터와 모든 출판 목록을 JSON으로 수집하는 파이썬 스크립트를 제공합니다.  
기본적으로 **프록시를 사용**하여 차단 위험을 낮추고, 실패 시 **자동 폴백(fallback)** 순서로 다른 방법을 시도합니다.

> 파일명 주의: 이 저장소의 스크립트는 `google_scholar_scrap.py` 입니다.  
> 코드 내 예시 문자열에 `google_scholar_scraper.py` 라는 이름이 등장하지만, 실제 파일명에 맞춰 사용하세요.

---

## ✨ 주요 기능

- 저자 프로필 메타데이터 수집 (이름, 소속, 이메일 도메인, 관심분야, 인용 수 등)
- 전체 출판물 목록 및 각 항목의 서지/인용 정보 수집
- 각 출판물에 대한 상세 정보 채우기(`scholarly.fill`)
- **프록시 자동 폴백**: `free → none → scraperapi → tor`
- 결과를 `output/author_{저자이름}.json` 으로 저장 (UTF-8, 들여쓰기 2)

---

## 📦 요구 사항

- Python 3.8 이상 권장
- 패키지
  - [`scholarly`](https://pypi.org/project/scholarly/) (Google Scholar 비공식 클라이언트)
- (선택) 프록시 관련 의존성
  - **TOR** 사용 시: 시스템에 Tor가 설치되어 있어야 합니다.
  - **ScraperAPI** 사용 시: 유효한 API Key

```bash
pip install scholarly
# (선택) macOS에서 tor
# brew install tor
# (선택) Debian/Ubuntu에서 tor
# sudo apt-get update && sudo apt-get install -y tor
```

---

## 🚀 빠른 시작 (TL;DR)

```bash
# 1) URL로 실행 (기본적으로 프록시 사용)
python3 google_scholar_scrap.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"

# 2) 프록시 없이 실행
python3 google_scholar_scrap.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en" --no-proxy

# 3) 저자 ID로 직접 실행 (URL 생략 가능)
python3 google_scholar_scrap.py --author-id ssXOHSoAAAAJ

# 4) 특정 프록시 방법 지정
python3 google_scholar_scrap.py "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en" \
  --proxy-method free

# 5) ScraperAPI 사용
python3 google_scholar_scrap.py --author-id ssXOHSoAAAAJ \
  --proxy-method scraperapi --scraperapi-key YOUR_API_KEY
```

> **쉘에서 URL에 `&` 가 포함되면 반드시 큰따옴표/작은따옴표로 감싸세요.**

---

## 🧰 커맨드라인 옵션

| 옵션 | 타입/값 | 기본값 | 설명 |
|---|---|---:|---|
| `url` | 문자열(선택) | — | Google Scholar 저자 프로필 URL. `--author-id` 를 주면 생략 가능 |
| `--author-id` | 문자열 | — | URL 파싱 없이 저자 ID 직접 지정 |
| `--no-proxy` | 플래그 | 사용 안 함 | 지정 시 **프록시 비활성화** (기본은 프록시 사용) |
| `--proxy-method` | `free` \| `scraperapi` \| `tor` \| `none` | `free` | 프록시 백엔드 선택 |
| `--scraperapi-key` | 문자열 | — | `scraperapi` 사용 시 필수 |

동작 원리 요약:

- 기본값은 프록시 사용이며, `--no-proxy` 를 주면 비활성화됩니다.
- `--proxy-method free`(기본)인 상태에서 프록시가 실패하면 순차적으로 **`free → none → scraperapi → tor`** 를 시도합니다.
- `--proxy-method` 를 `free` 이외로 지정하면 폴백 없이 해당 방법만 사용합니다.

---

## 🗂️ 출력 형식 & 저장 위치

- 저장 경로: `output/author_{저자이름_정규화}.json`
- 파일명 정규화: 공백은 `_`로, `/ \ : * ? " < > |` 등의 문자는 제거합니다.
- JSON 구조(요약):

```json
{
  "author": {
    "scholar_id": "...",
    "name": "...",
    "affiliation": "...",
    "email_domain": "...",
    "interests(label)": ["...", "..."],
    "citedby": 1234,
    "citedby5y": 789,
    "total_publications": 42
  },
  "articles": [
    {
      "title": "...",
      "authors": "...",
      "journal": "...",
      "year": "2021",
      "abstract": "...",
      "pages": "...",
      "num_citations": 12,
      "cited_by_url": "https://scholar.google.com/...",
      "pub_url": "https://...",
      "eprint_url": "https://...",
      "url_scholarbib": "https://scholar.google.com/...",
      "source": "scholar",
      "author_ids": ["ABCD...","EFGH..."],
      "fill_error": "상세 채우기 실패 시에만 존재"
    }
  ]
}
```

> 일부 필드는 Scholar 페이지에 값이 없으면 `null` 이 될 수 있습니다.  
> 각 출판물은 먼저 `scholarly.fill(pub)` 으로 상세정보를 채우며, 실패 시 최소 정보와 함께 `fill_error` 를 기록합니다.

---

## 🔌 내부 구성(개발자용)

- **`extract_author_id(url)`**: URL 쿼리의 `user` 파라미터에서 저자 ID 추출 (도메인/파라미터 순서/대소문자 변형 허용)
- **`setup_proxy(method, key)`**: `ProxyGenerator` 로 프록시 설정 (`free`, `scraperapi`, `tor`, `none`)
- **`_perform_scraping(author_id)`**: 실제 스크레이핑 로직 (저자 검색→기본정보/출판목록 채우기→논문별 상세 수집)
- **`try_scrape_with_fallback(author_id, methods, key)`**: 프록시 실패 시 `scholarly` 모듈 리로드 후 다음 방법 시도
- **`scrape_author(...)`**: 상위 오케스트레이션 (URL/ID 해석, 프록시 on/off 및 폴백 제어)
- **`sanitize_filename(name)`**: 결과 파일명 안전화
- **진입점**: `main()` — 인자 파싱, 출력 디렉터리 생성, JSON 저장

---

## 🧪 사용 팁

- **URL 대신 ID 사용**: 긴 URL을 복사/붙여넣기하기 번거롭다면 `--author-id` 를 쓰세요.
- **프록시 실패 시**:
  1) `--no-proxy` 를 한 번 시도  
  2) `--proxy-method scraperapi --scraperapi-key ...`  
  3) Tor 설치 후 `--proxy-method tor`
- **속도/안정성**: 무료 프록시는 느리거나 불안정할 수 있습니다. 빈번히 쓰면 유료 프록시가 유리합니다.
- **출력 정리**: 결과 JSON을 파이프라인에서 바로 가공해 CSV/파케이로 변환해도 좋습니다.

---

## 🛡️ 주의 & 윤리

- Google Scholar는 **자동화 트래픽을 제한**할 수 있습니다. 과도한 호출은 **HTTP 429** 나 차단으로 이어질 수 있습니다.
- Scholar/프록시/데이터 사용은 **해당 서비스 약관과 현지 법률**을 준수해야 합니다.
- 공개되지 않은 데이터를 유추/재배포하지 않도록 주의하세요.

---

## 🔍 문제 해결 (FAQ)

**Q. 429 / 차단이 자주 발생합니다.**  
A. 요청 간 대기 시간을 늘리고, 프록시 폴백을 활용하세요. 가능하면 ScraperAPI 같은 안정적 프록시를 고려하세요.

**Q. 일부 논문의 상세 정보가 비어 있습니다.**  
A. Scholar 페이지에 값이 없거나 `fill` 중 실패했을 수 있습니다. 이 경우 해당 항목에 `fill_error` 가 포함됩니다.

**Q. 결과 파일명이 이상합니다.**  
A. 파일명은 `sanitize_filename`으로 정규화합니다. 공백은 `_`, 위험 문자는 제거됩니다.

