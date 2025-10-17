#!/usr/bin/env python3
"""
저자의 모든 논문 제목을 나열하는 스크립트
"""

import sys
from pathlib import Path

# script 디렉토리를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "script"))

from lab import fetch_papers, load_config, HEADERS
import requests
from bs4 import BeautifulSoup
import time

def list_all_papers():
    """저자의 모든 논문 제목 나열"""
    print("=" * 80)
    print("저자의 모든 논문 제목 나열")
    print("=" * 80)

    # config에서 저자 프로필 URL 로드
    config = load_config()
    author_url = config.get('author_profile_url')

    if not author_url:
        print("❌ 오류: config.yaml에서 author_profile_url을 찾을 수 없습니다.")
        return

    print(f"\n저자 프로필 URL: {author_url}")
    print("\n논문 목록 가져오는 중...\n")

    # 모든 논문 링크 가져오기
    paper_links = fetch_papers(author_url)

    if not paper_links:
        print("\n❌ 논문 목록을 가져올 수 없습니다.")
        return

    print(f"\n총 {len(paper_links)}개의 논문 링크를 찾았습니다.")
    print("\n" + "=" * 80)
    print("논문 제목 목록:")
    print("=" * 80)

    paper_titles = []

    for idx, paper_link in enumerate(paper_links, 1):
        try:
            response = requests.get(paper_link, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 제목 추출
            title_elem = soup.find("div", id="gsc_oci_title")
            if title_elem:
                title = title_elem.text.strip()
                paper_titles.append(title)
                print(f"\n[{idx}] {title}")

            # 서버 부하 방지
            time.sleep(1)

        except Exception as e:
            print(f"\n[{idx}] ❌ 오류 발생: {e}")
            continue

    # 파일로 저장
    output_file = Path(__file__).parent / "output" / "all_paper_titles.txt"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"저자 프로필: {author_url}\n")
        f.write(f"총 논문 수: {len(paper_titles)}개\n")
        f.write("=" * 80 + "\n\n")

        for idx, title in enumerate(paper_titles, 1):
            f.write(f"[{idx}] {title}\n\n")

    print("\n" + "=" * 80)
    print(f"✓ 논문 제목 목록이 '{output_file}' 파일로 저장되었습니다.")
    print(f"✓ 총 {len(paper_titles)}개의 논문 제목")
    print("=" * 80)


if __name__ == "__main__":
    try:
        list_all_papers()
    except KeyboardInterrupt:
        print("\n\n⚠ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
