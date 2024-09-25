import os
import pandas as pd
import numpy as np
import requests
from math import radians, sin, cos, sqrt, atan2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import re
import json

# .env 파일에서 Kakao API 키 로드
load_dotenv()
kakao_api_key = os.getenv('KAKAO_API_KEY')

# 피드백 기록을 위한 파일
feedback_file = "feedback.json"

# 피드백 기록을 로드하는 함수
def load_feedback():
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r') as file:
            return json.load(file)
    return {}

# 피드백 기록을 저장하는 함수
def save_feedback(feedback_data):
    with open(feedback_file, 'w') as file:
        json.dump(feedback_data, file)

# Kakao API를 통해 입력된 주소를 구체적인 주소로 변환하고, 위도, 경도로 변환하는 함수
def get_lat_lon_from_address(address, api_key):
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    search_url = "https://dapi.kakao.com/v2/local/search/address.json"
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        documents = response.json().get('documents', [])
        if documents:
            latitude = float(documents[0]['y'])
            longitude = float(documents[0]['x'])
            full_address = documents[0]['address_name']
            return full_address, latitude, longitude
        else:
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None, None, None

# Haversine 공식을 사용해 두 지점 사이의 거리를 계산하는 함수 (km 단위)
def haversine(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    R = 6371.0  # 지구 반지름 (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# 불필요한 문장을 제거하고 주소만 추출하는 함수 (자연어 처리 적용)
def extract_address(text):
    text = re.sub(r'에 있어|에 위치해|에 있습니다', '', text)
    return text.strip()

# 텍스트 매칭을 위해 TF-IDF 기반으로 매칭 정확도를 계산하는 함수
def calculate_similarity(user_input, job_text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_input, job_text])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]

# 입력된 질문을 키워드로 분리하는 함수 (간단한 자연어 처리 적용)
def extract_keywords(text):
    # 질문을 소문자로 변환하고 불필요한 단어 제거
    text = text.lower().strip()
    keywords = re.findall(r'\b\w+\b', text)  # 단어만 추출
    return keywords

# 피드백을 반영한 우선순위 조정 함수
def adjust_priority_with_feedback(job, feedback_data):
    job_id = job['title']  # 타이틀을 고유 ID로 사용 (필요시 고유 ID를 생성)
    feedback = feedback_data.get(job_id, None)
    
    if feedback == '맞음':  # 과거 피드백에서 긍정적 응답
        job['priority_score'] -= 5  # 우선순위 점수를 크게 낮춤 (즉, 더 상위에 표시됨)
    elif feedback == '틀림':  # 부정적 응답
        job['priority_score'] += 5  # 우선순위 점수를 높임 (즉, 하위로 표시됨)
    
    return job

# JobSearchChatbot 클래스
class JobSearchChatbot:
    def __init__(self, job_data_file):
        self.df = pd.read_csv(job_data_file)
        self.feedback_data = load_feedback()  # 피드백 데이터 로드

    def find_jobs(self, user_input, user_lat, user_lon):
        keywords = extract_keywords(user_input)  # 입력된 질문을 키워드화
        
        matching_jobs = []

        # 각 일자리의 설명, 키워드, 제목과 사용자 키워드 매칭 (설명, 키워드, 제목 순으로 우선순위 적용)
        for _, row in self.df.iterrows():
            description = str(row['description']).lower()
            keywords_field = str(row['keywords']).lower()
            title = str(row['title']).lower()

            # 각각의 필드와 매칭되는 정도를 평가
            description_similarity = calculate_similarity(user_input, description)
            keywords_similarity = calculate_similarity(user_input, keywords_field)
            title_similarity = calculate_similarity(user_input, title)

            # 총 유사도 점수 (설명에 높은 가중치, 키워드와 제목은 낮은 가중치)
            total_similarity = (description_similarity * 0.5) + (keywords_similarity * 0.3) + (title_similarity * 0.2)

            if total_similarity > 0.1:  # 일정 수준 이상의 유사도만 처리
                job_lat, job_lon = row['latitude'], row['longitude']
                
                # 위도/경도가 없는 경우 건너뛰기
                if pd.isna(job_lat) or pd.isna(job_lon):
                    continue
                
                # 거리 계산
                distance = haversine(user_lat, user_lon, job_lat, job_lon)
                if distance is None:
                    distance = float('inf')  # 거리 정보가 없으면 무한대로 처리
                
                matching_jobs.append({
                    'title': row['title'],
                    'description': row['description'],
                    'address_name': row['address_name'],
                    'latitude': job_lat,
                    'longitude': job_lon,
                    'distance_km': distance,
                    'similarity': total_similarity  # 유사도 추가
                })

        # 거리 30km 이상이면 거리에 더 높은 가중치, 30km 이하면 유사도 우선
        for job in matching_jobs:
            if job['distance_km'] > 30:
                job['priority_score'] = job['distance_km'] * 0.7 + job['similarity'] * 0.3  # 거리 우선
            else:
                job['priority_score'] = job['similarity'] * 0.7 + job['distance_km'] * 0.3  # 유사도 우선

            # 피드백 데이터가 있는 경우 우선순위에 반영
            job = adjust_priority_with_feedback(job, self.feedback_data)

        # 우선순위 점수에 따라 정렬
        sorted_jobs = sorted(matching_jobs, key=lambda x: x['priority_score'])
        
        return sorted_jobs

    def generate_response(self, user_input, user_address):
        # 입력된 주소를 더 구체적으로 변환하고 위도, 경도 계산
        refined_address = extract_address(user_address)
        full_address, user_lat, user_lon = get_lat_lon_from_address(refined_address, kakao_api_key)
        if user_lat is None or user_lon is None:
            return "입력한 주소의 위치를 찾을 수 없습니다."

        # 사용자의 입력을 기반으로 가장 적합한 일자리 찾기
        filtered_jobs = self.find_jobs(user_input, user_lat, user_lon)

        if not filtered_jobs:
            return "입력한 키워드에 맞는 일자리가 없습니다."

        # 결과 응답 생성
        response = f"입력한 주소({full_address}) 기준으로 가까운 일자리를 찾았습니다:\n\n"
        for idx, job in enumerate(filtered_jobs[:5]):  # 상위 5개만 표시
            if isinstance(job['distance_km'], (int, float)):
                response += (f"{idx + 1}. **제목**: {job['title']}\n"
                             f"📋 **설명**: {job['description']}\n"
                             f"🏠 **주소**: {job['address_name']}\n"
                             f"📍 **거리**: {job['distance_km']:.2f}km 떨어져 있습니다.\n"
                             f"⚖️ **우선순위 점수**: {job['priority_score']:.2f}\n\n")

        if filtered_jobs:  # 응답이 있는 경우에만 피드백 요청
            # 사용자가 응답에 대해 맞는지 틀린지 피드백을 받을 수 있도록 추가
            for idx, job in enumerate(filtered_jobs[:5]):
                feedback = input(f"{idx + 1}. 이 일자리가 맞는 응답입니까? (맞음/틀림): ").strip()
                job_id = job['title']  # 타이틀을 ID로 사용
                if feedback == '맞음':
                    self.feedback_data[job_id] = '맞음'
                elif feedback == '틀림':
                    self.feedback_data[job_id] = '틀림'

            # 피드백 데이터를 저장
            save_feedback(self.feedback_data)

        return response

if __name__ == "__main__":
    job_data_file = 'job_data.csv'
    chatbot = JobSearchChatbot(job_data_file)

    while True:
        user_input = input("질문을 입력하세요 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            break
        user_address = input("사용자 주소를 입력하세요: ")
        response = chatbot.generate_response(user_input, user_address)
        print(response)
