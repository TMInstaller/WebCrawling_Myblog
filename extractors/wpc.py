# wpc.py
# = web page crawling
from requests import get
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_page_count(keyword):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=options)
    browser.get(f"https://www.kurly.com/search?sword={keyword}")
    browser.implicitly_wait(time_to_wait=3)
    pages = browser.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[3]').text
    # pages는 줄바꿈으로 이루어진 형태의 리스트이다
    # 1\n2\n3\n4\n5\n6\n7\n8\n9\n10
    pages = pages.splitlines()
    count = []
    # int형으로 모두 바꿔주고 최댓값 얻기
    for page in pages:
        count.append(int(page))
    count = max(count)
    # 10페이지 이상 넘어갈 수는 없으니 최대 10까지만 return한다
    if count >= 10:
        return 10
    else:
        return count


def extract_timemapexe_keys(keyword_b):
    url = "https://time-map-installer.tistory.com/search/"
    response = get(f"{url}{keyword_b}")
    if response.status_code != 200:
        print("페이지를 불러올 수 없습니다", response.status_code)
    else:
        results = []
        soup = BeautifulSoup(response.text, 'html.parser')
        keys = soup.find_all('div', class_='inner')
        for key_section in keys:
            key_posts = key_section.find_all('div', class_='post-item')
            for post in key_posts:
                span = post.find('a')
                title = span.find('span', class_='title')
                meta = span.find('span', class_='meta')
                date = meta.find('span', class_='date')
                excerpt = span.find('span', class_='excerpt')
                key_data = {
                    'title': title.string,
                    'date': date.string,
                    'prev': excerpt.string
                }
                results.append(key_data)
        return results


def extract_kurly_items(keyword_k):
    # 화면에 띄워져 있는 페이지의 최대 수를 검색하기 위한 코드
    pages = get_page_count(keyword_k)
    print("Found", pages, "pages")
    # 페이지 수 만큼 반복시키며 데이터를 가져오는 코드 실행
    results = []
    for page in range(1, pages+1):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        browser = webdriver.Chrome(options=options)
        url = 'https://www.kurly.com/search?sword='
        final_url = f"{url}{keyword_k}&page={page}"
        print("Requesting", final_url)
        browser.get(final_url)
        browser.implicitly_wait(time_to_wait=3)

        elements = browser.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[2]').text
        items = elements.split('\n샛별배송')
        items[0] = items[0][4:]
        elements_list = []
        for item in items:
            items = item.splitlines()
            elements_list.append(items)
        # 뭔가 문제가 생기면 아래 코드를 실행해보면 답이 나온다
        # print(elements_list)
        for element in elements_list:
            # 최대 고전 부분
            # 현재 element 의 길이가 4가 아닌 경우 불량인 배열이므로 폐기
            # 삭제 활용 시 리스트의 길이가 달라져서 실행 불가능
            if len(element) != 4:
                continue
            title = element[1]
            price = element[2].replace('%', '% 할인, ')
            memo = element[3]
            items_data = {
                '상품명': title,
                '가격': price,
                '상품 설명': memo,
            }
            results.append(items_data)
    return results


