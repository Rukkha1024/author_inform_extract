verify that the codebase reflects the plan.md file

============================

google_scholar_scraper.py 는 plan.md 파일의 내용을 반영한다. codebase를 살펴보고 plan.md 파일의 내용을 제대로 반영하고 있는지 확인하라.

google_scholar_scraper.py는 절대로 수정하면 안된다. 
==============
default 저장 경로는 output 폴더여야 한다. 없으면 생성해라.

proxy 설정은 `  conda run -n author_extract python script/google_scholar_scraper.py \
    "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"` 실행 시, ` --use-proxy --proxy-method free` 가 default 옵션이 되도록 하라.