import requests
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, tostring

# author_url 예시: https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en
def fetch_papers(author_url):
    paper_links = []
    response = requests.get(author_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 논문별 상세페이지 링크 추출
    for a in soup.select('a[href^="/citations?view_op=view_citation"]'):
        paper_links.append("https://scholar.google.com" + a["href"])
    return paper_links

def fetch_paper_detail(paper_url):
    response = requests.get(paper_url)
    soup = BeautifulSoup(response.text, "html.parser")
    # 예시: 논문 정보 추출 (실제 태그는 페이지 구조에 따라 달라집니다)
    title = soup.find("div", class_="title-class").text
    authors = [a.text for a in soup.select(".author-class")]
    pub_date = soup.find("span", class_="date-class").text
    abstract = soup.find("div", class_="abstract-class").text

    # XML 구조 생성
    article = Element('Article')
    SubElement(article, "Title").text = title
    authors_elem = SubElement(article, "Authors")
    for name in authors:
        SubElement(authors_elem, "Author").text = name
    SubElement(article, "PublicationDate").text = pub_date
    SubElement(article, "Description").text = abstract
    return article

def main(author_url):
    xml_root = Element("Articles")
    for paper_url in fetch_papers(author_url):
        article_xml = fetch_paper_detail(paper_url)
        xml_root.append(article_xml)
    xml_string = tostring(xml_root, encoding="unicode")
    return xml_string

author_url = "https://scholar.google.com/citations?user=ssXOHSoAAAAJ&hl=en"
print(main(author_url))
