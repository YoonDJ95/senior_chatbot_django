import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv

# .env 파일에서 Kakao API 키 로드
load_dotenv()
kakao_api_key = os.getenv('KAKAO_API_KEY')

# Kakao API를 통해 업체명을 기반으로 주소, 위도, 경도를 가져오는 함수
def get_address_and_lat_lon_from_title(title, api_key):
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": title}  # 업체명을 검색어로 사용
    search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        documents = response.json().get('documents', [])
        if documents:
            # 첫 번째 검색 결과에서 주소와 위도, 경도를 추출
            address_name = documents[0].get('address_name', '주소 없음')
            latitude = float(documents[0].get('y', 0))
            longitude = float(documents[0].get('x', 0))
            return address_name, latitude, longitude
        else:
            return '주소 없음', None, None  # 검색 결과가 없는 경우
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return '주소 없음', None, None

# task와 키워드를 추출하는 함수
def extract_task_and_keywords(description):
    task = "업무 없음"
    keywords = []

    # Task 추출: "담당업무"라는 키워드 이후의 텍스트를 추출
    if "담당업무" in description:
        task = description.split("담당업무 :")[-1].split('*')[0].strip()
    
    # 키워드 추출: 단순한 텍스트에서 키워드를 추출하는 방식
    keywords = [word.strip() for word in description.split() if len(word) > 2]  # 두 글자 이상인 키워드들
    return task, keywords

# 실제 크롤링을 수행하는 함수
def crawl_data(base_url, start_page, end_page):
    data = []
    
    for page in range(start_page, end_page + 1):
        url = f"{base_url}&pageIndex={page}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for row in soup.find_all('tr'):
                title_tag = row.find('a', class_='cp_name underline_hover')
                description_tag = row.find('span', class_='item')

                if title_tag and description_tag:
                    title = title_tag.text.strip()
                    description = description_tag.text.strip()

                    # Task 및 키워드 추출
                    task, keywords = extract_task_and_keywords(description)

                    # 업체명을 통해 주소, 위도, 경도를 가져오기
                    address_name, lat, lon = get_address_and_lat_lon_from_title(title, kakao_api_key)

                    
                    data.append({
                        'title': title,
                        'description': description,
                        'task': task,
                        'keywords': ', '.join(keywords),
                        'address_name': address_name,
                        'latitude': lat,
                        'longitude': lon,
                    })

            print(f"Page {page} 크롤링 완료")
        except Exception as e:
            print(f"오류 발생: {e}, URL: {url}")
    
    # 데이터를 CSV로 저장
    df = pd.DataFrame(data)
    df.to_csv('job_data.csv', index=False, encoding='utf-8-sig')
    print("크롤링 완료 및 csv 파일 저장 완료")

if __name__ == "__main__":
    base_url = "https://m.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?resultCnt=50"  # 실제 URL로 변경
    start_page = 1
    end_page = 65

    crawl_data(base_url, start_page, end_page)
