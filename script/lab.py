import sys
import os
from pathlib import Path
import yaml
import requests
from bs4 import BeautifulSoup
import json
import time

# Selenium imports (Show more 버튼 클릭을 위해)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError as e:
    SELENIUM_AVAILABLE = False
    print(f"경고: Selenium 또는 webdriver-manager가 설치되어 있지 않습니다.")
    print(f"   모든 논문을 가져오려면 'pip install selenium webdriver-manager'를 실행하세요.")
    print(f"   오류 세부정보: {e}")


# 설정 파일 경로
CONFIG_DIR = Path(__file__).parent.parent
CONFIG_FILE = CONFIG_DIR / "config.yaml"

def load_config():
    """config.yaml 파일에서 설정 로드"""
    if not CONFIG_FILE.exists():
        print(f"오류: config.yaml 파일을 찾을 수 없습니다: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

# 설정 로드
CONFIG = load_config()

# User-Agent 헤더 추가 (Google Scholar 접근을 위해 필수)
HEADERS = {
    'User-Agent': CONFIG.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
}

def fetch_papers_selenium(author_url):
    """Selenium을 사용해 'Show more' 버튼을 클릭하여 모든 논문 링크 추출"""
    if not SELENIUM_AVAILABLE:
        print("❌ 오류: Selenium이 설치되어 있지 않습니다.")
        print("   'pip install selenium'을 실행하여 설치해주세요.")
        return []

    # URL에서 user ID 추출
    if 'user=' in author_url:
        user_id = author_url.split('user=')[1].split('&')[0]
    else:
        print("오류: 유효한 저자 프로필 URL이 아닙니다.")
        return []

    print(f"저자 ID: {user_id}")
    print("브라우저를 시작하고 논문 목록을 가져오는 중...")

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'user-agent={CONFIG.get("user_agent")}')

    driver = None
    paper_links = []

    try:
        # WebDriver 초기화 (시스템에 설치된 chromedriver 사용)
        # webdriver-manager 버전 문제로 시스템 chromedriver 직접 사용
        import shutil
        chromedriver_path = shutil.which('chromedriver')

        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            # fallback: webdriver-manager 사용
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(author_url)

        print("  페이지 로딩 중...")
        time.sleep(3)  # 초기 로딩 대기

        # "Show more" 버튼을 클릭할 수 없을 때까지 반복
        click_count = 0
        max_clicks = 50  # 무한 루프 방지

        while click_count < max_clicks:
            try:
                # "Show more" 버튼 찾기
                # HTML: <span class="gs_wr"><span class="gs_ico"></span><span class="gs_lbl">Show more</span></span>
                # 또는 button#gsc_bpf_more
                show_more_button = None

                # 방법 1: button ID로 찾기
                try:
                    show_more_button = driver.find_element(By.ID, "gsc_bpf_more")
                except NoSuchElementException:
                    pass

                # 방법 2: 클래스와 텍스트로 찾기
                if not show_more_button:
                    try:
                        show_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'gs_btn_lsb') and contains(., 'Show more')]")
                    except NoSuchElementException:
                        pass

                # 방법 3: span 요소로 찾기
                if not show_more_button:
                    try:
                        show_more_button = driver.find_element(By.XPATH, "//span[@class='gs_lbl' and contains(text(), 'Show more')]")
                    except NoSuchElementException:
                        pass

                # 버튼을 찾지 못하거나 비활성화되어 있으면 종료
                if not show_more_button:
                    print(f"  'Show more' 버튼을 찾을 수 없습니다. (클릭 {click_count}회 완료)")
                    break

                # 버튼이 비활성화되어 있는지 확인
                if show_more_button.get_attribute("disabled"):
                    print(f"  'Show more' 버튼이 비활성화되었습니다. (클릭 {click_count}회 완료)")
                    break

                # 버튼 클릭
                driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", show_more_button)
                click_count += 1
                print(f"  'Show more' 버튼 클릭 ({click_count}회)...")

                # 새로운 논문이 로드될 때까지 대기
                time.sleep(2)

            except Exception as e:
                print(f"  'Show more' 버튼 클릭 중 오류 발생: {e}")
                break

        print(f"\n  'Show more' 버튼을 {click_count}회 클릭했습니다.")
        print("  논문 링크 추출 중...")

        # 페이지 소스를 가져와서 파싱
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # 논문 링크 추출
        paper_elements = soup.select('a.gsc_a_at')

        for a in paper_elements:
            href = a.get('data-href') or a.get('href')
            if href:
                full_url = "https://scholar.google.com" + href if not href.startswith("http") else href
                paper_links.append(full_url)

        print(f"\n총 {len(paper_links)}개의 논문 링크를 찾았습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()

    return paper_links


def fetch_papers(author_url):
    """저자 프로필 페이지에서 모든 논문 링크 추출 (Selenium 우선, 실패 시 기본 방식)"""
    # Selenium 사용 시도
    if SELENIUM_AVAILABLE:
        print("\n[Selenium 모드] 'Show more' 버튼을 자동으로 클릭하여 모든 논문을 가져옵니다.")
        return fetch_papers_selenium(author_url)

    # Selenium이 없으면 기본 방식 사용
    print("\n[기본 모드] Selenium이 없어 페이지네이션 방식으로 논문을 가져옵니다.")
    print("주의: 'Show more' 버튼 뒤에 숨겨진 논문은 가져올 수 없습니다.")
    return fetch_papers_basic(author_url)


def fetch_papers_basic(author_url):
    """저자 프로필 페이지에서 논문 링크 추출 (기본 방식 - 페이지네이션)"""
    paper_links = []

    # URL에서 user ID 추출
    if 'user=' in author_url:
        user_id = author_url.split('user=')[1].split('&')[0]
    else:
        print("오류: 유효한 저자 프로필 URL이 아닙니다.")
        return []

    print(f"저자 ID: {user_id}")
    print("논문 목록을 가져오는 중...")

    # 페이지네이션 처리
    page_size = 100  # 한 번에 가져올 논문 수
    start_index = 0

    while True:
        try:
            # list_works 페이지로 요청 (모든 논문을 보여주는 페이지)
            url = f"https://scholar.google.com/citations?user={user_id}&hl=en&cstart={start_index}&pagesize={page_size}&view_op=list_works&sortby=pubdate"

            print(f"  페이지 요청 중... (시작 인덱스: {start_index})")
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 논문별 상세페이지 링크 추출
            paper_elements = soup.select('a.gsc_a_at')

            if not paper_elements:
                # 더 이상 논문이 없으면 종료
                print(f"  페이지에 논문이 없습니다. 수집 완료.")
                break

            page_count = 0
            for a in paper_elements:
                href = a.get('data-href') or a.get('href')
                if href:
                    full_url = "https://scholar.google.com" + href if not href.startswith("http") else href
                    paper_links.append(full_url)
                    page_count += 1

            print(f"  ✓ {page_count}개의 논문 링크를 추가했습니다.")

            # 다음 페이지가 있는지 확인
            if page_count < page_size:
                # 가져온 논문 수가 page_size보다 작으면 마지막 페이지
                print(f"  마지막 페이지입니다.")
                break

            start_index += page_size

            # Google Scholar 서버 부하 방지를 위한 대기
            time.sleep(2)

        except Exception as e:
            print(f"논문 링크 추출 중 오류 발생: {e}")
            break

    print(f"\n총 {len(paper_links)}개의 논문 링크를 찾았습니다.")
    return paper_links

def fetch_author_profile(author_url):
    """저자 프로필 페이지에서 저자 정보 추출"""
    try:
        response = requests.get(author_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        profile = {}

        # 저자 이름 추출
        name_elem = soup.find("div", id="gsc_prf_in")
        if name_elem:
            profile["name"] = name_elem.text.strip()

        # 소속 기관 추출
        org_elem = soup.find("a", class_="gsc_prf_ila")
        if org_elem:
            profile["institution"] = org_elem.text.strip()

        # 이메일 및 홈페이지 추출
        email_div = soup.find("div", id="gsc_prf_ivh")
        if email_div:
            email_text = email_div.text.strip()
            # "Verified email at udel.edu - Homepage" 형식에서 이메일 추출
            if "Verified email at" in email_text:
                email_part = email_text.split("Verified email at")[1].split("-")[0].strip()
                profile["verified_email"] = email_part

            # 홈페이지 링크 추출
            homepage_link = email_div.find("a", class_="gsc_prf_ila")
            if homepage_link and homepage_link.get("href"):
                profile["homepage"] = homepage_link.get("href")

        # 연구 관심사 추출
        interests_div = soup.find("div", id="gsc_prf_int")
        if interests_div:
            interest_links = interests_div.find_all("a", class_="gsc_prf_inta")
            if interest_links:
                profile["research_interests"] = [link.text.strip() for link in interest_links]

        print(f"✓ 저자 프로필 정보 추출 완료: {profile.get('name', 'N/A')}")
        return profile

    except Exception as e:
        print(f"⚠ 저자 프로필 정보 추출 실패: {e}")
        return {}


def fetch_paper_detail(paper_url, retry_count=3):
    """논문 상세 페이지에서 정보 추출 (재시도 기능 포함)"""
    for attempt in range(retry_count):
        try:
            response = requests.get(paper_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 제목 추출
            title_elem = soup.find("div", id="gsc_oci_title")
            title = title_elem.text.strip() if title_elem else "N/A"

            # 메타데이터 추출 (Authors, Journal, Publication date, etc.)
            metadata = {}
            fields = soup.find_all("div", class_="gsc_oci_field")
            values = soup.find_all("div", class_="gsc_oci_value")

            for field, value in zip(fields, values):
                field_name = field.text.strip()
                field_value = value.text.strip()
                metadata[field_name] = field_value

            # 초록/설명 추출
            abstract_elem = soup.find("div", class_="gsc_oci_merged_snippet")
            abstract = abstract_elem.text.strip() if abstract_elem else "N/A"

            # 인용 수 추출
            citations = "N/A"
            for field, value in zip(fields, values):
                if "Total citations" in field.text:
                    citations = value.text.strip()
                    break

            # 외부 논문 링크 추출 (실제 출판사 사이트 링크)
            external_url = None
            external_link_div = soup.find("div", class_="gsc_oci_title_ggi")
            if external_link_div:
                external_link_a = external_link_div.find("a")
                if external_link_a and external_link_a.get("href"):
                    external_url = external_link_a.get("href")

            # JSON 구조 생성 (dictionary)
            article = {
                "title": title,
                "authors": [],
                "google_scholar_url": paper_url
            }

            # 외부 링크가 있으면 추가
            if external_url:
                article["external_url"] = external_url

            # 저자 정보
            if "Authors" in metadata:
                article["authors"] = [author.strip() for author in metadata["Authors"].split(", ")]

            # 발행 정보
            if "Publication date" in metadata:
                article["publication_date"] = metadata["Publication date"]

            if "Journal" in metadata:
                article["journal"] = metadata["Journal"]

            if "Volume" in metadata:
                article["volume"] = metadata["Volume"]

            if "Pages" in metadata:
                article["pages"] = metadata["Pages"]

            if "Publisher" in metadata:
                article["publisher"] = metadata["Publisher"]

            # 인용 수
            if citations != "N/A":
                article["citations"] = citations

            # 기타 메타데이터
            other_metadata = {}
            for key, value in metadata.items():
                if key not in ["Authors", "Publication date", "Journal", "Volume", "Pages", "Publisher"]:
                    other_metadata[key.replace(" ", "_")] = value

            if other_metadata:
                article["other_metadata"] = other_metadata

            # 초록
            article["abstract"] = abstract

            print(f"  ✓ 추출 완료: {title[:60]}...")

            # 서버 부하 방지를 위한 대기
            time.sleep(1)

            return article

        except Exception as e:
            if attempt < retry_count - 1:
                print(f"  ⚠ 오류 발생 (재시도 {attempt + 1}/{retry_count}): {e}")
                time.sleep(3)
            else:
                print(f"  ✗ 논문 상세 정보 추출 실패 ({paper_url}): {e}")
                return None

    return None

def main(author_url_or_papers):
    """메인 실행 함수"""
    result = {"papers": []}

    # 단일 논문 URL이 입력된 경우
    if isinstance(author_url_or_papers, str) and "view_op=view_citation" in author_url_or_papers:
        print("\n" + "=" * 80)
        print("단일 논문 처리 모드")
        print("=" * 80)
        article = fetch_paper_detail(author_url_or_papers)
        if article is not None:
            result["papers"].append(article)

    # 저자 프로필 URL이 입력된 경우
    elif isinstance(author_url_or_papers, str):
        print("\n" + "=" * 80)
        print("저자 프로필 처리 모드")
        print("=" * 80)

        # 저자 프로필 정보 추출
        print("\n저자 프로필 정보 추출 중...")
        author_profile = fetch_author_profile(author_url_or_papers)
        if author_profile:
            result["author_profile"] = author_profile

        # 논문 목록 가져오기
        paper_urls = fetch_papers(author_url_or_papers)

        if not paper_urls:
            print("\n⚠ 논문을 찾을 수 없습니다.")
            return json.dumps(result, ensure_ascii=False, indent=2)

        print(f"\n논문 상세 정보 추출 시작 (총 {len(paper_urls)}개)")
        print("-" * 80)

        success_count = 0
        fail_count = 0

        for idx, paper_url in enumerate(paper_urls, 1):
            print(f"[{idx}/{len(paper_urls)}] 처리 중...")
            article = fetch_paper_detail(paper_url)
            if article is not None:
                result["papers"].append(article)
                success_count += 1
            else:
                fail_count += 1

        print("-" * 80)
        print(f"\n처리 완료: 성공 {success_count}개 / 실패 {fail_count}개")

    # 논문 URL 리스트가 입력된 경우
    elif isinstance(author_url_or_papers, list):
        print("\n" + "=" * 80)
        print("논문 리스트 처리 모드")
        print("=" * 80)
        print(f"총 {len(author_url_or_papers)}개의 논문 처리 예정")
        print("-" * 80)

        success_count = 0
        fail_count = 0

        for idx, paper_url in enumerate(author_url_or_papers, 1):
            print(f"[{idx}/{len(author_url_or_papers)}] 처리 중...")
            article = fetch_paper_detail(paper_url)
            if article is not None:
                result["papers"].append(article)
                success_count += 1
            else:
                fail_count += 1

        print("-" * 80)
        print(f"\n처리 완료: 성공 {success_count}개 / 실패 {fail_count}개")

    return json.dumps(result, ensure_ascii=False, indent=2)

# 테스트 모드: config.yaml의 저자 프로필 URL로 테스트
if __name__ == "__main__":
    print("=" * 80)
    print("Google Scholar 논문 정보 추출 테스트 (저자 프로필 모드)")
    print("=" * 80)
    print()

    # config에서 저자 프로필 URL 로드
    author_url = CONFIG.get('author_profile_url')

    if not author_url:
        print("오류: config.yaml에서 author_profile_url을 찾을 수 없습니다.")
        print("단일 논문 테스트로 전환합니다...")

        # 대체: 단일 논문 URL로 테스트
        test_paper_url = CONFIG.get('test_paper_url')
        if not test_paper_url:
            print("오류: config.yaml에서 test_paper_url도 찾을 수 없습니다.")
            sys.exit(1)

        author_url = test_paper_url

    # output 폴더 생성
    output_dir = CONFIG_DIR / CONFIG.get('output_dir', 'output')
    output_dir.mkdir(exist_ok=True)

    print(f"입력 URL: {author_url}")
    print()

    try:
        # 논문 정보 추출 실행
        result_json = main(author_url)

        print("\n" + "=" * 80)
        print("추출된 JSON (처음 500자 미리보기):")
        print("=" * 80)
        print(result_json[:500] + "...")

        # JSON 파일로 저장
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"test_{timestamp}.json"
        output_path = output_dir / output_filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_json)

        print("\n" + "=" * 80)
        print(f"✓ 결과가 '{output_path}' 파일로 저장되었습니다.")
        print(f"✓ 파일 크기: {output_path.stat().st_size / 1024:.2f} KB")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
