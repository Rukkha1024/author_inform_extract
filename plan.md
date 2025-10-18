
**목표:**

사용자는 특정 Google Scholar 연구자(저자)의 구글 스칼라 프로필(예: `https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en`)을 입력하면, 해당 저자가 출판한 **모든 논문의 세부 정보를 자동으로 추출**하고, 이를 **통일된 json 형식의 데이터로 일괄 정리**하고자 합니다.

**상세 설명:**

- **입력:** 
  - cli 형태의 입력
  - Google Scholar 저자 페이지 링크(Author Profile URL)를 변수로 입력
- **출력:** 
  - 저자가 출판한 모든 논문(학술 논문, 리뷰 등)의 상세정보 (예: 제목, 저자, 저널명, 출판연도, 초록(요약), 학술지, 페이지 번호, 인용 수, 링크 등)
  - 결과는 논문별로 체계적으로 정리된 JSON 문서 형태 (예시에서 보인 Article 단위 등, 각 논문을 `<Article>`로 감싸는 방식)
- **자동화 방법:** 전체 과정을 파이썬 스크립트로 자동화해, 사용자는 단순히 저자 링크만 넣으면 결과를 받을 수 있도록 한다.
- **활용 목적:** 
  - 연구자의 publication portfolio를 한눈에 정리
  - 출판 통계, 개인 연구 관리, 문헌 관리, 시스템 데이터 이관 등 다양한 상황에 데이터 활용 가능
- **추가 조건:** 
  - 논문 수가 많더라도 누락 없이 전체 논문을 지원
  - 논문 정보의 정확성(실제 논문 상세 링크, 저자 정보 등)과 일관성(포맷, 항목 등) 보장
  - 새로운 저자에 대해서도 같은 방식으로 적용 가능
- "<span class="gs_wr"><span class="gs_ico"></span><span class="gs_lbl">Show more</span></span>" 해당 부분을 클릭할 수 없을 때까지 논문의 리스트를 만든 후, 추출을 시작해야 한다. 
- "<div class="gsc_oci_title_ggi"><a href="https://www.frontiersin.org/articles/10.3389/fspor.2021.788165/full" data-clk="hl=en&amp;sa=T&amp;ei=Y0vzaIW_K_LJieoPv_CRkAU"><span class="gsc_vcd_title_ggt">[HTML]</span> from frontiersin.org</a></div>" 의 "href" 링크도 json output에 저장되어야 한다. 
- output에는 논문 저자의 내용도 포함되어야 한다. 
  - 해당 부분의 예시: "<div id="gsc_prf_i"><div id="gsc_prf_inw"><div id="gsc_prf_in">Jeremy R. Crenshaw</div></div><div class="gsc_prf_il"><a href="/citations?view_op=view_org&amp;hl=en&amp;org=9340941294191691364" class="gsc_prf_ila">University of Delaware</a></div><div class="gsc_prf_il" id="gsc_prf_ivh">Verified email at udel.edu - <a href="http://sites.udel.edu/kaap/crenshaw-lab/" rel="nofollow" class="gsc_prf_ila">Homepage</a></div><div class="gsc_prf_il" id="gsc_prf_int"><a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:falls" class="gsc_prf_inta gs_ibl">Falls</a><a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:gait" class="gsc_prf_inta gs_ibl">Gait</a><a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:balance" class="gsc_prf_inta gs_ibl">Balance</a><a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:stability" class="gsc_prf_inta gs_ibl">Stability</a><a href="/citations?view_op=search_authors&amp;hl=en&amp;mauthors=label:biomechanics" class="gsc_prf_inta gs_ibl">Biomechanics</a></div></div>" 

***

즉, **일일이 논문을 복사·붙여넣기하지 않고, 저자별 논문정보 전체를 시스템적으로 수집/가공하여, 원하는 형식(JSON 등)으로 한 번에 볼 수 있도록 자동화하는 것**이 당신의 최종 목적입니다.

[1](https://scholar.google.com/citations?view_op=list_works&hl=en&hl=en&user=ssXOHSoAAAAJ&sortby=pubdate)