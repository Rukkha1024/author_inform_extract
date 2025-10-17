#!/usr/bin/env python3
"""
Google Scholar 논문 정보 추출 도구
Author Profile URL을 입력하면 모든 논문 정보를 XML로 추출합니다.

사용법:
    python extract_papers.py <author_profile_url>
    python extract_papers.py https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en

또는 대화형 모드:
    python extract_papers.py
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# script 디렉토리를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "script"))

from lab import main, load_config


def print_banner():
    """배너 출력"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║      Google Scholar 논문 정보 추출 도구                                  ║
║      Paper Information Extractor from Google Scholar                     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_author_url_from_user():
    """사용자로부터 대화형으로 저자 프로필 URL 입력받기"""
    print("\n저자 프로필 URL을 입력해주세요.")
    print("예시: https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en")
    print("-" * 79)

    while True:
        author_url = input("\n저자 프로필 URL: ").strip()

        if not author_url:
            print("❌ URL을 입력해주세요.")
            continue

        if "scholar.google.com" not in author_url or "user=" not in author_url:
            print("❌ 올바른 Google Scholar 저자 프로필 URL이 아닙니다.")
            print("   URL에 'user=' 파라미터가 포함되어 있는지 확인해주세요.")
            retry = input("\n다시 입력하시겠습니까? (y/n): ").strip().lower()
            if retry != 'y':
                print("\n프로그램을 종료합니다.")
                sys.exit(0)
            continue

        return author_url


def save_xml_result(xml_content, output_dir, author_url):
    """XML 결과를 파일로 저장"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # 파일명 생성 (저자 ID + 타임스탬프)
    user_id = author_url.split('user=')[1].split('&')[0] if 'user=' in author_url else "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}.xml"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_content)

    return filepath


def main_cli():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        description="Google Scholar 저자의 모든 논문 정보를 XML 형식으로 추출합니다.",
        epilog="예시: python extract_papers.py https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
    )

    parser.add_argument(
        "author_url",
        nargs="?",
        help="Google Scholar 저자 프로필 URL"
    )

    parser.add_argument(
        "-o", "--output",
        default="output",
        help="출력 디렉토리 경로 (기본값: output)"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="진행 상황 출력 최소화"
    )

    args = parser.parse_args()

    # 배너 출력
    if not args.quiet:
        print_banner()

    # 저자 URL 가져오기
    if args.author_url:
        author_url = args.author_url
    else:
        author_url = get_author_url_from_user()

    # URL 유효성 검사
    if "scholar.google.com" not in author_url or "user=" not in author_url:
        print("\n❌ 오류: 올바른 Google Scholar 저자 프로필 URL이 아닙니다.")
        print("   URL에 'user=' 파라미터가 포함되어 있는지 확인해주세요.")
        sys.exit(1)

    print(f"\n저자 프로필 URL: {author_url}")
    print("=" * 79)

    # 논문 정보 추출 실행
    try:
        xml_result = main(author_url)

        if not xml_result or "<Article>" not in xml_result:
            print("\n⚠ 경고: 추출된 논문 정보가 없습니다.")
            sys.exit(1)

        # 결과 저장
        output_path = save_xml_result(xml_result, args.output, author_url)

        print("\n" + "=" * 79)
        print("✓ 모든 작업이 완료되었습니다!")
        print(f"✓ 결과 파일: {output_path}")
        print(f"✓ 파일 크기: {output_path.stat().st_size / 1024:.2f} KB")
        print("=" * 79)

        # XML 미리보기 (처음 500자)
        if not args.quiet:
            print("\n[XML 미리보기 - 처음 500자]")
            print("-" * 79)
            print(xml_result[:500] + "...")
            print("-" * 79)

    except KeyboardInterrupt:
        print("\n\n⚠ 사용자에 의해 중단되었습니다.")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
