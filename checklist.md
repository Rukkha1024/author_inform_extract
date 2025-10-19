verify that the codebase reflects the plan.md file
===========================
google_scholar_scraper.py 는 plan.md 파일의 내용을 반영한다. codebase를 살펴보고 plan.md 파일의 내용을 제대로 반영하고 있는지 확인하라.

google_scholar_scraper.py는 절대로 수정하면 안된다. 
==============
create git commit specifically in korean 

==============================
<!-- - [ ] 프록시 문제 해결 
  - [ ] free가 default 
  - [ ] free 안될 시 순차적으로 use the option: none -> scraperapi -> tor -->
<!-- - [ ] 현재 docstring 제거. 새롭게 docstring 작성. 
  - [ ] 옵션은 docstring에 명시 
  - [ ] docstring에 사용법 명시 -->
<!-- - [ ] config.yaml 필요한지 검토: 필요 없다  -->
<!-- - [ ] "6d36cb8c013b1736ba7610be32b6c22e69f53279" 이전에 한 내용 중 wsl2에 설치된 것들 모두 제거. python package, 기타 프로그램(크롬 등) -->
- [ ] 다양한 링크를 사용해 접속시 안되는 현상 발생 
  - [ ] "https://scholar.google.co.kr/citations?hl=en&user=hdV_QJMAAAAJ&view_op=list_works&citft=1&citft=2&citft=3&email_for_op=dreaming.rukkha%40gmail.com&authuser=1&sortby=pubdate" 
  - [ ] "https://scholar.google.co.kr/citations?hl=en&authuser=1&user=S3U3BcAAAAAJ"
  - [ ] "https://scholar.google.com/citations?hl=en&user=eFGnK9QAAAAJ&view_op=list_works&citft=1&citft=2&email_for_op=dreaming.rukkha%40gmail.com&authuser=1&gmla=AC6lMd_uAMSOsSGRXk_I6cOk5VKH6HvfA7xzK_M_0Dga6F9oDTcx5I7hEtPxPhtdScG4AQBH2jaaWK-o5pNcrMirfZFkfdPcdVZm8lvSrtWXEVgecyju8ZFAp7iPRwLeCzfNLocMy_ulT61tiV7jwzGvF4m3ttQlVMoM48H34yVeEAt3F6_bTHCobMMEJF-m3T7RpZ0jQhzcpMoMf_Yqfnxp69rgmR3_hPQr4wbKhKoRoHVvEDD1kZ56NNKd_etiC3icoNSISYk"
- [ ] review the `modified code scholar.py` & `URL 문제 해결 요청.pdf` file and check the `google_scholar_scraper.py` code's logic still remain in `modified code scholar.py` file. 