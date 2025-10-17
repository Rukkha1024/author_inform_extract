#!/usr/bin/env python3
"""
저자의 논문 제목을 빠르게 확인하는 스크립트 (상세 페이지 방문 없이 목록 페이지에서만)
"""

import sys
from pathlib import Path

# script 디렉토리를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "script"))

from lab import load_config, HEADERS
import requests
from bs4 import BeautifulSoup

def quick_list_papers():
    """저자의 논문 제목을 빠르게 나열 (목록 페이지에서만)"""
    print("=" * 80)
    print("저자의 논문 제목 빠른 확인 (목록 페이지)")
    print("=" * 80)

    # config에서 저자 프로필 URL 로드
    config = load_config()
    author_url = config.get('author_profile_url')

    if not author_url:
        print("❌ 오류: config.yaml에서 author_profile_url을 찾을 수 없습니다.")
        return

    print(f"\n저자 프로필 URL: {author_url}")

    # URL에서 user ID 추출
    if 'user=' in author_url:
        user_id = author_url.split('user=')[1].split('&')[0]
    else:
        print("오류: 유효한 저자 프로필 URL이 아닙니다.")
        return

    print(f"저자 ID: {user_id}")
    print("\n논문 목록 가져오는 중...\n")

    paper_titles = []
    page_size = 100
    start_index = 0

    # list_works 페이지에서 제목 추출
    url = f"https://scholar.google.com/citations?user={user_id}&hl=en&cstart={start_index}&pagesize={page_size}&view_op=list_works&sortby=pubdate"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 논문 제목 추출 (목록 페이지에서 직접)
        paper_elements = soup.select('a.gsc_a_at')

        print("=" * 80)
        print(f"논문 제목 목록 (총 {len(paper_elements)}개):")
        print("=" * 80)

        for idx, elem in enumerate(paper_elements, 1):
            title = elem.text.strip()
            paper_titles.append(title)
            print(f"\n[{idx}] {title}")

        # 파일로 저장
        output_file = Path(__file__).parent / "output" / "paper_titles_quick.txt"
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"저자 프로필: {author_url}\n")
            f.write(f"저자 ID: {user_id}\n")
            f.write(f"총 논문 수: {len(paper_titles)}개\n")
            f.write("=" * 80 + "\n\n")

            for idx, title in enumerate(paper_titles, 1):
                f.write(f"[{idx}] {title}\n\n")

        print("\n" + "=" * 80)
        print(f"✓ 논문 제목 목록이 '{output_file}' 파일로 저장되었습니다.")
        print(f"✓ 총 {len(paper_titles)}개의 논문 제목")
        print("=" * 80)

        # 찾고자 하는 논문 검색
        target_title = "Walking shoes and laterally wedged orthoses in the clinical management of medial tibiofemoral osteoarthritis"
        target_title_lower = target_title.lower()

        print("\n" + "=" * 80)
        print("목표 논문 검색:")
        print("=" * 80)
        print(f"검색어: '{target_title}'")

        found = False
        for idx, title in enumerate(paper_titles, 1):
            # 부분 일치 검색
            if "walking shoes" in title.lower() or "wedged orthoses" in title.lower():
                print(f"\n✓ 유사한 논문 발견!")
                print(f"  [{idx}] {title}")
                found = True

        if not found:
            print("\n❌ 유사한 논문을 찾을 수 없습니다.")
            print("\n가능한 원인:")
            print("  1. 해당 논문이 이 저자의 프로필에 없음")
            print("  2. 논문 제목이 다르게 표시됨")
            print("  3. 저자가 다름")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        quick_list_papers()
    except KeyboardInterrupt:
        print("\n\n⚠ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
