verify that the codebase reflects the plan.md file

============================


(author_extract) alice@DESKTOP-S6GN0HU:/mnt/c/Users/alice/OneDrive - 청주대학교/VScode_R
epository/author_inform_extract$ python3 extract_papers.py "https://scholar.google.com/c
itations?user=ssXOHSoAAAAJ&hl=en"
       

저자 프로필 정보 추출 중...
⚠ 저자 프로필 정보 추출 실패: 429 Client Error: Too Many Requests for url: https://www.google.com/sorry/index?continue=https://scholar.google.com/citations%3Fuser%3DssXOHSoAAAAJ%26hl%3Den&hl=en&q=EgTTqE6MGK7KzccGIi4UfM6Aj7mZY5n67olN3yPmG_T1Wj0g_wL8IvALDYzK4FVkOV3F7bDmkcLH8if9MgJyUloBQw

----
find a way to handle rate limiting by searching internet. 