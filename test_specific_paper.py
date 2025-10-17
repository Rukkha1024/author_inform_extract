#!/usr/bin/env python3
"""
특정 논문이 추출되는지 테스트하는 스크립트
"""

import sys
from pathlib import Path

# script 디렉토리를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "script"))

from lab import fetch_papers, fetch_paper_detail, load_config, HEADERS
import requests
from bs4 import BeautifulSoup

# 찾고자 하는 논문 제목
TARGET_PAPER_TITLE = "Walking shoes and laterally wedged orthoses in the clinical management of medial tibiofemoral osteoarthritis: a one-year prospective controlled trial"

def test_paper_extraction():
    """특정 논문이 추출되는지 테스트"""
    print("=" * 80)
    print("특정 논문 추출 테스트")
    print("=" * 80)
    print(f"\n찾고자 하는 논문:")
    print(f"  '{TARGET_PAPER_TITLE}'")
    print("\n" + "=" * 80)

    # config에서 저자 프로필 URL 로드
    config = load_config()
    author_url = config.get('author_profile_url')

    if not author_url:
        print("❌ 오류: config.yaml에서 author_profile_url을 찾을 수 없습니다.")
        return False

    print(f"\n저자 프로필 URL: {author_url}")
    print("\n" + "-" * 80)
    print("1단계: 논문 목록 가져오기")
    print("-" * 80)

    # 모든 논문 링크 가져오기
    paper_links = fetch_papers(author_url)

    if not paper_links:
        print("\n❌ 논문 목록을 가져올 수 없습니다.")
        return False

    print(f"\n✓ 총 {len(paper_links)}개의 논문 링크를 찾았습니다.")

    # 논문 제목 검색
    print("\n" + "-" * 80)
    print("2단계: 논문 목록에서 제목 검색")
    print("-" * 80)

    found_paper = None
    target_title_lower = TARGET_PAPER_TITLE.lower()

    # 각 논문 링크에서 간단히 제목만 추출해서 검색
    # (상세 정보 추출 전에 빠르게 확인)
    print("\n논문 제목 스캔 중...")

    for idx, paper_link in enumerate(paper_links, 1):
        try:
            response = requests.get(paper_link, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 제목 추출
            title_elem = soup.find("div", id="gsc_oci_title")
            if title_elem:
                title = title_elem.text.strip()

                # 진행 상황 출력 (매 10개마다)
                if idx % 10 == 0:
                    print(f"  [{idx}/{len(paper_links)}] 검색 중...")

                # 제목이 일치하는지 확인 (대소문자 구분 없이)
                if target_title_lower in title.lower() or title.lower() in target_title_lower:
                    found_paper = {
                        'title': title,
                        'link': paper_link,
                        'index': idx
                    }
                    print(f"\n✓ 논문을 찾았습니다! (인덱스: {idx}/{len(paper_links)})")
                    break

            # 서버 부하 방지
            import time
            time.sleep(1)

        except Exception as e:
            if idx % 10 == 0:
                print(f"  [{idx}/{len(paper_links)}] 검색 중... (일부 오류 발생)")
            continue

    if not found_paper:
        print(f"\n❌ 논문을 찾을 수 없습니다.")
        print(f"\n검색된 논문 수: {len(paper_links)}개")
        print("\n가능한 원인:")
        print("  1. 해당 논문이 이 저자의 프로필에 없음")
        print("  2. 논문 제목이 정확하지 않음")
        print("  3. Google Scholar에서 제목이 다르게 표시됨")
        return False

    print("\n" + "-" * 80)
    print("3단계: 논문 상세 정보 추출")
    print("-" * 80)

    print(f"\n발견된 논문 제목:")
    print(f"  '{found_paper['title']}'")
    print(f"\n논문 링크:")
    print(f"  {found_paper['link']}")

    print("\n상세 정보 추출 중...")
    article_xml = fetch_paper_detail(found_paper['link'])

    if article_xml is None:
        print("\n❌ 논문 상세 정보를 추출할 수 없습니다.")
        return False

    # XML 미리보기
    from xml.etree.ElementTree import tostring
    xml_string = tostring(article_xml, encoding="unicode")

    print("\n" + "=" * 80)
    print("✓ 성공! 논문 정보가 추출되었습니다.")
    print("=" * 80)

    print("\n추출된 XML (미리보기):")
    print("-" * 80)
    print(xml_string[:800] + "...")
    print("-" * 80)

    # XML 파일로 저장
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"specific_paper_test_{timestamp}.xml"
    output_path = output_dir / output_filename

    # XML 포맷팅
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"\n✓ 결과가 '{output_path}' 파일로 저장되었습니다.")

    return True


if __name__ == "__main__":
    try:
        success = test_paper_extraction()
        if success:
            print("\n" + "=" * 80)
            print("✓✓✓ 테스트 완료: 시스템이 정상적으로 작동합니다! ✓✓✓")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ 테스트 실패")
            print("=" * 80)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
