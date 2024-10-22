import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import math
from datetime import datetime


# 위도와 경도를 이용하여 두 지점 사이의 거리를 계산하는 함수
def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371.0  # 지구의 반경 (km)
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)

    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# 카카오 API를 통해 주소로부터 위도와 경도 정보를 얻는 함수
def get_lat_lng_from_address(address):
    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_API_KEY}",
    }
    params = {
        "query": address,
    }
    response = requests.get(f"https://dapi.kakao.com/v2/local/search/address.json", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if len(data['documents']) > 0:
            return float(data['documents'][0]['y']), float(data['documents'][0]['x'])  # 위도, 경도 반환
    return None, None

# 채용 정보 검색 함수
def get_closest_job_info(user_lat, user_lng, title, employment_type):
    params = {
        "serviceKey": settings.PUBLIC_DATA_API_KEY,
        "recrtTitle": title,
        "emplymShp": employment_type,
        "pageNo": '1',
        "numOfRows": '1000'  # 최대 100개의 채용정보를 가져옴
    }
    response = requests.get('http://apis.data.go.kr/B552474/SenuriService/getJobList', params=params)

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            jobs = []
            
            for item in root.findall('.//item'):
                # 각 필드를 찾아서 None이 아닌지 먼저 확인한 후 .text에 접근
                recrtTitle = item.find('recrtTitle').text if item.find('recrtTitle') is not None else '정보 없음'
                workPlcNm = item.find('workPlcNm').text if item.find('workPlcNm') is not None else '정보 없음'
                oranNm = item.find('oranNm').text if item.find('oranNm') is not None else '정보 없음'
                frDd = item.find('frDd').text if item.find('frDd') is not None else '정보 없음'
                toDd = item.find('toDd').text if item.find('toDd') is not None else '정보 없음'
                emplymShpNm = item.find('emplymShpNm').text if item.find('emplymShpNm') is not None else '정보 없음'
                acptMthd = item.find('acptMthd').text if item.find('acptMthd') is not None else '정보 없음'
                deadline = item.find('deadline').text if item.find('deadline') is not None else '정보 없음'
                jobId = item.find('jobId').text if item.find('jobId') is not None else None  # jobId 추가

                if deadline == "마감":
                    continue

                job = {
                    "recrtTitle": recrtTitle,
                    "workPlcNm": workPlcNm,
                    "oranNm": oranNm,
                    "frDd": frDd,
                    "toDd": toDd,
                    "emplymShpNm": map_emplymShpNm(emplymShpNm),
                    "acptMthd": acptMthd,
                    "deadline": deadline,
                    "jobId": jobId,
                }

                # 근무지명의 위도와 경도를 가져오기
                work_lat, work_lng = get_lat_lng_from_address(job['workPlcNm'])

                # 근무지 좌표를 찾은 경우 거리를 계산
                if work_lat and work_lng:
                    distance = calculate_distance(user_lat, user_lng, work_lat, work_lng)
                    if distance <= 30:  # 30km 이내인 경우에만 추가
                        job['distance'] = distance  # 거리를 추가
                        jobs.append(job)

            # 거리 순으로 정렬 후 가까운 10개의 채용정보를 반환
            jobs = sorted(jobs, key=lambda x: x['distance'])[:10]

            return {"data": jobs}

        except ET.ParseError:
            print("Error parsing XML response.")
            return {"error": "응답을 파싱하는 데 문제가 발생했습니다."}
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return {"error": "채용 정보 API에서 데이터를 가져오는 데 문제가 발생했습니다."}

def map_emplymShpNm(emplymShpNm):
    return{
        'CM0101':'정규직',
        'CM0102':'계약직',
        'CM0103':'시간제일자리',
        'CM0104':'일당직',
        'CM0105':'기타'
    }.get(emplymShpNm, '정보 없음')

def map_acptMthdCd(acptMthdCd):
    return {
        'CM0801':'온라인',
        'CM0802':'이메일',
        'CM0803':'팩스',
        'CM0804':'방문'

    }.get(acptMthdCd, '정보 없음')

def map_organYn(organYn):
    return {
        'N': '대민',
        'Y': '업무'
    }.get(organYn, '정보 없음')

def map_stmId(stmId):
    return {
        'A': '100세누리',
        'B': '워크넷',
        'C': '일모아'
    }.get(stmId, '정보 없음')
    
    
def map_lnkStmId(lnkStmId):
    return {
        'A': '100세누리',
        'B': '워크넷',
        'C': '일모아'
    }.get(lnkStmId, '정보 없음')

def convert_to_am_pm(iso_date):
    if iso_date == '정보 없음':
        return '정보 없음'
    
    try:
        # ISO 8601 형식의 문자열을 datetime 객체로 변환
        date_obj = datetime.fromisoformat(iso_date)
        # 한국어 형식으로 AM/PM 시간 표시 변환
        am_pm_format = date_obj.strftime('%Y년 %m월 %d일  %p %I시 %M분')
        # AM/PM을 소문자로 변경
        return am_pm_format
    except ValueError:
        return '잘못된 날짜 형식'

def format_date(date_str):
    if not date_str or date_str == '정보 없음':
        return '정보 없음'

    # 'YYYYMMDD' 형식의 문자열을 'xxxx년 xx월 xx일'로 변환
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%Y년 %m월 %d일')
    except ValueError:
        return '정보 없음'
    
# 채용 공고 상세 정보 조회 함수
def get_job_detail(job_id):
    params = {
        "serviceKey": settings.PUBLIC_DATA_API_KEY,  # 공공데이터포털에서 발급받은 인증키
        "id": job_id  # 조회할 채용 공고의 ID
    }
    response = requests.get('http://apis.data.go.kr/B552474/SenuriService/getJobInfo', params=params)

    if response.status_code == 200:
        try:
            #print("API 응답 데이터:", response.text)
            root = ET.fromstring(response.content)

            # 상세 정보 항목들 추출
            acptMthdCd = root.find('.//acptMthdCd').text if root.find('.//acptMthdCd') is not None else '정보 없음'
            age = root.find('.//age').text if root.find('.//age') is not None else '정보 없음'
            ageLim = root.find('.//ageLim').text if root.find('.//ageLim') is not None else '정보 없음'
            clerk = root.find('.//clerk').text if root.find('.//clerk') is not None else '정보 없음'
            clerkContt = root.find('.//clerkContt').text if root.find('.//clerkContt') is not None else '정보 없음'
            clltPrnnum = root.find('.//clltPrnnum').text if root.find('.//clltPrnnum') is not None else '정보 없음'
            createDy = root.find('.//createDy').text if root.find('.//createDy') is not None else '정보 없음'
            detCnts = root.find('.//detCnts').text if root.find('.//detCnts') is not None else '정보 없음'
            etcItm = root.find('.//etcItm').text if root.find('.//etcItm') is not None else '정보 없음'
            frAcptDd = root.find('.//frAcptDd').text if root.find('.//frAcptDd') is not None else '정보 없음'
            homepage = root.find('.//homepage').text if root.find('.//homepage') is not None else '정보 없음'
            jobId = root.find('.//jobId').text if root.find('.//jobId') is not None else '정보 없음'
            lnkStmId = root.find('.//lnkStmId').text if root.find('.//lnkStmId') is not None else '정보 없음'
            organYn = root.find('.//organYn').text if root.find('.//organYn') is not None else '정보 없음'
            plDetAddr = root.find('.//plDetAddr').text if root.find('.//plDetAddr') is not None else '정보 없음'
            plbizNm = root.find('.//plbizNm').text if root.find('.//plbizNm') is not None else '정보 없음'
            repr = root.find('.//repr').text if root.find('.//repr') is not None else '정보 없음'
            stmId = root.find('.//stmId').text if root.find('.//stmId') is not None else '정보 없음'
            toAcptDd = root.find('.//toAcptDd').text if root.find('.//toAcptDd') is not None else '정보 없음'
            updDy = root.find('.//updDy').text if root.find('.//updDy') is not None else '정보 없음'
            wantedAuthNo = root.find('.//wantedAuthNo').text if root.find('.//wantedAuthNo') is not None else '정보 없음'
            wantedTitle = root.find('.//wantedTitle').text if root.find('.//wantedTitle') is not None else '정보 없음'

            # 상세 정보 딕셔너리로 반환
            job_detail = {
                "acptMthdCd": map_acptMthdCd(acptMthdCd),
                "age": age,
                "ageLim": ageLim,
                "clerk": clerk,
                "clerkContt": clerkContt,
                "clltPrnnum": clltPrnnum,
                "createDy": convert_to_am_pm(createDy),
                "detCnts": detCnts,
                "etcItm": etcItm,
                "frAcptDd": format_date(frAcptDd),
                "homepage": homepage,
                "jobId": jobId,
                "lnkStmId": map_lnkStmId(lnkStmId),
                "organYn": map_organYn(organYn),
                "plDetAddr": plDetAddr,
                "plbizNm": plbizNm,
                "repr": repr,
                "stmId": map_stmId(stmId),
                "toAcptDd": format_date(toAcptDd),
                "updDy": convert_to_am_pm(updDy),
                "wantedAuthNo": wantedAuthNo,
                "wantedTitle": wantedTitle,
            }

            return {"data": job_detail}

        except ET.ParseError:
            print("Error parsing XML response.")
            return {"error": "응답을 파싱하는 데 문제가 발생했습니다."}
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return {"error": "채용 정보 API에서 데이터를 가져오는 데 문제가 발생했습니다."}



# 상세 채용 공고 정보 제공 API
def job_detail_view(request, job_id):
    job_detail = get_job_detail(job_id)  # 채용 공고 상세 정보 가져오기
    if "error" in job_detail:
        return JsonResponse({"error": job_detail["error"]}, status=500)
    return JsonResponse(job_detail)  # JSON 형태로 데이터 반환


# 챗봇 요청 처리 함수
def chatbot_response(request):
    try:
        user_input = request.GET.get('message', '')
        user_address = request.GET.get('user_address', '')

        # 사용자 입력 파싱
        title, employment_type, workplace = parse_user_input(user_input)

        # 사용자의 거주지 위도, 경도 가져오기
        user_lat, user_lng = get_lat_lng_from_address(user_address)
        if not user_lat or not user_lng:
            return JsonResponse({"error": "사용자의 거주지 정보를 찾을 수 없습니다."}, status=400)

        # 가까운 채용정보 검색
        job_info = get_closest_job_info(user_lat, user_lng, title, employment_type)

        return JsonResponse({"job_info": job_info})

    except Exception as e:
        # 예외가 발생할 경우 에러 로그를 출력하고 JSON 에러 메시지를 반환
        print(f"Error occurred: {e}")
        return JsonResponse({"error": "서버 처리 중 에러가 발생했습니다."}, status=500)


# 입력 문자열을 파싱하는 함수
def parse_user_input(user_input):
    parts = user_input.split(",")
    title = parts[0].strip() if len(parts) > 0 else ""
    employment_type = parts[1].strip() if len(parts) > 1 else ""
    workplace = parts[2].strip() if len(parts) > 2 else ""
    
    return title, employment_type, workplace

# 메인 페이지 렌더링
def index(request):
    return render(request, 'chatbot/index.html')
def home(request):
    return render(request, 'chatbot/home.html')  # home.html을 렌더링
# 카카오 API 키를 반환하는 함수
def get_kakao_api_key(request):
    return JsonResponse({'apiKey': settings.KAKAO_API_KEY})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SearchHistory
import json

@csrf_exempt  # CSRF 보호를 우회, 실제 운영에서는 적절한 방법으로 처리
def save_search_history(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        search_query = data.get('search_query')
        results = data.get('results')  # 결과 메시지 추가
        user = request.user

        if user.is_authenticated and search_query:
            print(f"Saving search history for user: {user.username}, Query: {search_query}, Results: {results}")
            SearchHistory.objects.create(
                user=user,
                search_query=search_query,
                search_results=results  # 저장할 때 결과도 추가
            )
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


# 사용자별 검색 기록 보기
def search_history(request):
    if request.user.is_authenticated:
        history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')
        # 이 부분에서 검색 결과도 함께 가져올 수 있도록 개선
        for record in history:
            # 예시: record.search_results에 저장된 검색 결과를 여기에 불러오는 로직 추가
            pass
        return render(request, 'chatbot/search_history.html', {'history': history})
    else:
        return redirect('login')  # 로그인되지 않은 경우 로그인 페이지로 리다이렉트


from django.contrib.auth.decorators import login_required

@login_required
def clear_search_history(request):
    if request.method == 'POST':
        SearchHistory.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)