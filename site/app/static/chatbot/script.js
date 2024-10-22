document.addEventListener("DOMContentLoaded", function () {
    const userAddressInput = document.getElementById("userAddress");

    userAddressInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // 설명 메시지를 초기화면에 표시
    const introMessage = `
        <div>
            안녕하세요! 저는 채용 정보 안내 챗봇입니다.<br>
            아래 입력창에 주소를 입력하시면, 해당 지역에서 30km 이내의 채용 정보를 최대 10건까지 알려드릴게요.<br>
            시작하려면 거주지를 입력해 주세요.
            ex) 동탄 / 수원 / 화성 / 해운대 / 강남 등
        </div>
    `;
    addMessageToChat(introMessage, 'bot'); // 설명 메시지를 'bot'으로 추가
});

// 페이지 로드 시 API 키 가져오기
fetch('/get_kakao_api_key/')
    .then(response => response.json())
    .then(data => {
        apiKey = data.apiKey; // API 키 저장
        console.log("API 키가 성공적으로 로드되었습니다.");
    })
    .catch(error => {
        console.error('API 키 로드 오류:', error);
    });

var endLat, endLng;  // 전역 변수로 선언

function sendMessage() {
    const userAddress = document.getElementById("userAddress").value; // 사용자의 주소
    console.log(`${userAddress} 와 가까운 업체들을 찾습니다.`); // 로그 추가
    if (!userAddress) {
        return addMessageToChat("사용자 또는 근무지의 주소를 입력하지 않으셨어요"); // 빈 메시지일 경우 실행 중단
    }

    // 사용자 메시지 추가
    addMessageToChat(`거주하는 주소: ${userAddress}`, 'user');
    addMessageToChat(`${userAddress} 인근의 구인정보를 탐색중입니다...`, 'bot');

    // 사용자 주소를 서버로 전송
    fetch(`/chatbot/?user_address=${encodeURIComponent(userAddress)}`)
        .then(response => response.json())
        .then(data => {
            // 데이터가 올바르게 있는지 확인
            if (data && data.job_info && data.job_info.data && data.job_info.data.length > 0) {
                let combinedMessage = "";  // combinedMessage 초기화

                data.job_info.data.forEach(job => {
                    // 각 채용 정보에서 jobId 확인
                    console.log("보낸 Job ID:", job.jobId); // Job ID 확인
                    let jobMessage = `
                        <div class="job-card">
                        <div class="job-title">${job.recrtTitle || '정보 없음'}</div>
                        <div>근무지명: ${job.workPlcNm || '정보 없음'}</div>
                        <div>사업장명: ${job.oranNm || '정보 없음'}</div>
                        ${job.emplymShpNm ? `<div>고용형태: ${job.emplymShpNm}</div>` : ''}
                        ${job.acptMthd ? `<div>접수방법: ${job.acptMthd}</div>` : ''}
                        ${job.deadline ? `<div>마감여부: ${job.deadline}</div>` : ''}
                        ${job.jobclsNm ? `<div>직종: ${job.jobclsNm}</div>` : ''}
                        </div>
                    `;

                    // 거리 계산 및 길찾기 링크 추가
                    if (job.jobId) {
                        // `calculateDistanceAndLink`에 `jobId`를 포함해서 전달
                        calculateDistanceAndLink(userAddress, job.workPlcNm, job.oranNm, jobMessage, job.jobId);
                    }

                    // jobMessage를 combinedMessage에 추가
                    combinedMessage += jobMessage;
                });

                // 검색 기록 저장
                console.log('검색 기록 저장을 위한 요청을 보냅니다.'); // 요청 전 로그 추가
                // 검색 기록 저장 부분
                fetch('/save-search-history/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken  // CSRF 토큰 추가
                    },
                    body: JSON.stringify({
                        search_query: userAddress,  // 사용자가 입력한 주소
                        results: combinedMessage  // HTML 형식의 결과 메시지
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('네트워크 응답이 올바르지 않습니다.');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);
                })
                
                .catch(error => {
                    console.error('AJAX 요청 오류:', error);
                });
            } else {
                addMessageToChat("해당 지역의 채용 정보를 찾을 수 없습니다.", 'bot');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat("챗봇에 문제가 발생했습니다.", 'bot');
        });

    // 입력창 초기화
    document.getElementById("userAddress").value = '';
}

// JSON 데이터를 HTML로 변환
/*const prettyJson = JSON.stringify(jsonResponse, null, 2); // Pretty print 적용
console.log(prettyJson);*/


function updateSearchHistoryDisplay() {
    fetch('/search-history/')
        .then(response => {
            // 응답이 HTML이 아닌 JSON인지 확인
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // JSON으로 변환
        })
        .then(data => {
            const historyContainer = document.getElementById("search-history-container");
            historyContainer.innerHTML = ''; // 기존 내용을 지우기
            data.history.forEach(record => {
                const recordElement = document.createElement("div");
                recordElement.innerHTML = `${record.search_query} - ${record.search_date}`;
                historyContainer.appendChild(recordElement);
            });
        })
        .catch(error => console.error('검색 기록 가져오기 오류:', error));
}



function calculateDistanceAndLink(startAddress, endAddress, jobTitle, jobMessage, jobId, index) { // jobId 추가
    console.log("가져온 Job ID:", jobId); // jobId가 올바르게 전달되는지 확인
    console.log("거리 계산 및 로드뷰 설정 중...");

    // 1. 출발지 주소로 위도, 경도 가져오기
    fetch(`https://dapi.kakao.com/v2/local/search/address.json?query=${encodeURIComponent(startAddress)}`, {
        headers: {
            Authorization: `KakaoAK ${apiKey}`,
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.documents.length === 0) {
                console.log("출발지 주소가 없습니다.");
                return;
            }

            const startLocation = data.documents[0];
            const startLat = startLocation.y;
            const startLng = startLocation.x;

            // 2. 근무지 주소(endAddress)를 이용하여 거리 계산
            fetch(`https://dapi.kakao.com/v2/local/search/address.json?query=${encodeURIComponent(endAddress)}`, {
                headers: {
                    Authorization: `KakaoAK ${apiKey}`,
                }
            })
                .then(response => response.json())
                .then(data => {
                    let combinedMessage = jobMessage;

                    if (data.documents.length === 0) {
                        console.log("근무지 주소를 찾을 수 없습니다.");
                        const noAddressMessage = `<div>근무지 주소를 찾을 수 없습니다.</div>`;
                        combinedMessage += noAddressMessage;
                        addMessageToChat(combinedMessage, 'bot');
                    } else {
                        // 근무지 좌표 사용 (거리 계산용)
                        const endLocation = data.documents[0];
                        const endLat = endLocation.y;
                        const endLng = endLocation.x;

                        // 고유한 버튼 ID 생성
                        const uniqueButtonId = `select-btn-${index}-${jobTitle.replace(/\s+/g, '')}-${jobId}-${endLat}-${endLng}`;
                        const selectButtonHtml = `<button id="${uniqueButtonId}" class="button1">로드뷰 보기</button>`;

                        // 상세내용 보기 버튼 추가 - jobId를 전달
                        const detailButtonHtml = `<button class="button1" onclick="showJobDetail('${jobId}')">상세내용 보기</button>`;

                        // 거리 정보와 선택 버튼 추가
                        const distance = getDistanceFromLatLonInKm(startLat, startLng, endLat, endLng);
                        const distanceMessage = `
                    <div>근무지역 중심까지의 거리: ${distance.toFixed(2)} km</div>
                    <div class="button-container" style="display: inline-block;">
                        ${selectButtonHtml}
                        ${detailButtonHtml}  <!-- 상세내용 보기 버튼 -->
                    </div>
                `;
                        combinedMessage += distanceMessage;

                        // 기업 소개와 거리 정보를 함께 출력
                        addMessageToChat(combinedMessage, 'bot');

                        // 3. 사업장명을 이용하여 로드뷰 설정
                        fetch(`/job_detail/${jobId}`)
                            .then(response => response.json())
                            .then(detailData => {
                                const jobDetail = detailData.data;
                                const cleanedAddress = jobDetail.plDetAddr
                                    ? jobDetail.plDetAddr
                                        .replace(/^\d{5}\s?/, '')
                                        .replace(/\s?\(.*?\)/, '')
                                        .replace(/,.*$/, '')
                                        //.replace(/(.*?(시|도)\s.*?(구|군|읍|면)\s?.*?(로|길|번길)\d*(\s?\d+(-\d+)?)?)/, '$1')
                                        .trim()
                                    : '정보 없음';
                                console.log(cleanedAddress)
                                fetch(`https://dapi.kakao.com/v2/local/search/keyword.json?query=${encodeURIComponent(cleanedAddress)}`, {
                                    headers: {
                                        Authorization: `KakaoAK ${apiKey}`,
                                    }
                                })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.documents.length === 0) {
                                            console.log("사업장 로드뷰를 찾을 수 없습니다.");

                                            // 로드뷰가 없을 때 버튼 대신 문구 출력
                                            const noCompanyMessage = `<div>사업장 로드뷰를 찾을 수 없습니다.</div>`;
                                            document.getElementById(uniqueButtonId).outerHTML = noCompanyMessage; // 버튼 대신 문구로 대체
                                            return;
                                        }

                                        // 사업장 좌표 사용 (로드뷰용)
                                        const companyLocation = data.documents[0];
                                        const companyLat = companyLocation.y;
                                        const companyLng = companyLocation.x;

                                        // 버튼 클릭 시 이벤트 리스너 등록 (로드뷰용)
                                        setTimeout(() => {
                                            const addedButton = document.getElementById(uniqueButtonId);

                                            if (addedButton) {
                                                addedButton.addEventListener('click', function () {
                                                    console.log(`선택 버튼을 눌렀음: ${jobTitle}, 회사 좌표: ${companyLat}, ${companyLng}`);
                                                    handleSelectButtonClick(companyLat, companyLng, cleanedAddress); // 로드뷰 업데이트
                                                });
                                            } else {
                                                console.error("버튼을 찾을 수 없습니다.");
                                            }
                                        }, 100); // 버튼이 DOM에 완전히 추가될 때까지 약간의 지연을 줍니다.

                                    })
                                    .catch(error => {
                                        console.error("사업장 로드뷰 API 오류:", error);

                                        // 로드뷰 API 오류 시 버튼 대신 문구 출력
                                        const noRoadViewMessage = `<div>사업장 로드뷰를 찾을 수 없습니다.</div>`;
                                        document.getElementById(uniqueButtonId).outerHTML = noRoadViewMessage; // 버튼 대신 문구로 대체
                                    });
                            })
                            .catch(error => {
                                console.error("상세 정보 API 오류:", error);
                            });
                    }
                })
                .catch(error => {
                    console.error("근무지 주소 API 오류:", error);
                    let combinedMessage = jobMessage + `<div>근무지 주소를 찾을 수 없습니다.</div>`;
                    addMessageToChat(combinedMessage, 'bot');
                });
        })
        .catch(error => {
            console.error("출발지 주소 API 오류:", error);
        });
}

function showJobDetail(jobId) {
    // 팝업 창 열기
    const popup = window.open("", "jobDetailPopup", "width=700,height=750,resizable=no,scrollbars=no");

    // 팝업 창의 기존 내용을 지우고 새로 갱신할 수 있도록 처리
    popup.document.open(); // 문서 초기화
    popup.document.write(`<html><head><title>상세내용 보기</title></head><body><p>로딩 중...</p></body></html>`);
    popup.document.close();

    // API 호출을 통해 상세정보 가져오기
    fetch(`/job_detail/${jobId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();  // JSON 형식으로 응답을 기대
        })
        .then(data => {
            if (data.error) {
                popup.document.open(); // 문서 초기화
                popup.document.write(`<p>상세 정보를 불러오는 중 오류가 발생했습니다.</p>`);
                popup.document.close();
            } else {
                const jobDetail = data.data;

                // 팝업 창 내용 설정
                popup.document.open(); // 문서 초기화
                popup.document.write(`
                    <html>
                    <head>
                        <title>상세내용 보기</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                padding: 20px;
                                background-color: #f9f9f9;
                                color: #333;
                            }
                            h1 {
                                font-size: 28px;
                                color: #007bff;
                                text-align: center;
                            }
                            p {
                                font-size: 16px;
                                margin: 10px 0;
                                line-height: 1.6;
                            }
                            .job-detail-container {
                                background-color: white;
                                padding: 20px;
                                border-radius: 8px;
                                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                                max-width: 650px;
                                margin: 0 auto;
                            }
                            .job-detail-container strong {
                                color: #007bff;
                            }
                            .job-detail-container a {
                                color: #007bff;
                                text-decoration: none;
                            }
                            .job-detail-container a:hover {
                                text-decoration: underline;
                            }
                            .job-detail-container hr {
                                border: 0;
                                border-top: 1px solid #ccc;
                                margin: 20px 0;
                            }
                            .phone-section {
                                display: flex;
                                align-items: center;
                                margin-top: 10px;
                            }
                            .phone-icon {
                                margin-right: 5px;
                            }
                            .call-button {
                                margin-left: 10px;
                                padding: 5px 10px;
                                background-color: #007bff;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                            }
                            .call-button:hover {
                                background-color: #0056b3;
                            }
                            .close-button-container {
                                display: flex;
                                justify-content: center;
                                margin-top: 20px;
                            }
                            .close-button {
                                padding: 10px 20px;
                                background-color: #dc3545;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                            }
                            .close-button:hover {
                                background-color: #c82333;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="job-detail-container">
                            <h1>상세 내용</h1>
                            <p><strong>채용제목:</strong> ${jobDetail.wantedTitle || '정보 없음'}</p>
                            <p><strong>사업장명:</strong> ${jobDetail.plbizNm || '정보 없음'}</p>
                            <p><strong>주소:</strong> ${jobDetail.plDetAddr || '정보 없음'}</p>
                            ${jobDetail.clerkContt && jobDetail.clerkContt !== '정보 없음' ? `
                                <div class="phone-section">
                                    <strong>담당자 연락처:</strong>
                                    <span> ${jobDetail.clerkContt}</span>
                                    <button class="call-button" onclick="location.href='tel:${jobDetail.clerkContt.replace(/\s+/g, '')}'">전화걸기</button>
                                </div>` : ''}
                            <p><strong>모집인원:</strong> ${jobDetail.clltPrnnum || '정보 없음'}</p>
                            ${jobDetail.detCnts !== '정보 없음' && jobDetail.detCnts ? `<p><strong>상세내용:</strong> ${jobDetail.detCnts}</p>` : ''}
                            <p><strong>우대사항:</strong> ${jobDetail.etcItm || '우대사항 없음'}</p>
                            <p><strong>접수방법:</strong> ${jobDetail.acptMthdCd || '정보 없음'}</p>
                            ${jobDetail.homepage !== '정보 없음' && jobDetail.homepage ? `<p><strong>홈페이지:</strong> <a href="${jobDetail.homepage}" target="_blank">${jobDetail.homepage}</a></p>` : ''}
                            <p><strong>담당자:</strong> ${jobDetail.clerk || '정보 없음'}</p>
                            ${jobDetail.ageLim ? `<p><strong>나이 제한:</strong> ${jobDetail.ageLim}</p>` : ''}
                            <p><strong>시작 접수일:</strong> ${jobDetail.frAcptDd || '정보 없음'}</p>
                            <p><strong>종료 접수일:</strong> ${jobDetail.toAcptDd || '정보 없음'}</p>
                
                            <hr>
                            <p><em>데이터는 최신 기준으로 제공됩니다.</em></p>
                            <p><strong>게시글 등록일:</strong> ${jobDetail.createDy || '정보 없음'}</p>
                            <p><strong>게시글 갱신일:</strong> ${jobDetail.updDy || '정보 없음'}</p>
                        </div>
                        <div class="close-button-container">
                            <button class="close-button" onclick="window.close()">닫기</button>
                        </div>
                    </body>
                    </html>
                `);
                popup.document.close();
                popup.onload = function () {
                    const newHeight = popup.document.body.scrollHeight + 50; // 내용에 맞게 높이 조절 (약간 여유있게)
                    popup.resizeTo(700, newHeight);
                };
            }
        })
        .catch(error => {
            console.error('Error fetching job detail:', error);
            popup.document.open(); // 문서 초기화
            popup.document.write(`<p>상세 정보를 불러오는 중 오류가 발생했습니다.</p>`);
            popup.document.close();
        });
}



// 거리 계산 함수
function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
    const R = 6371; // 지구 반지름 (km)
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // 거리 반환
}

// 도 단위 변환 함수
function deg2rad(deg) {
    return deg * (Math.PI / 180);
}



// 채팅 메시지 추가 함수
function addMessageToChat(message, sender) {
    const chatContainer = document.getElementById("chat-container");

    // 새로운 메시지 요소 생성
    const messageElement = document.createElement("div");
    messageElement.className = sender === 'user' ? "message user-message" : "message bot-message";
    messageElement.innerHTML = message;

    // 채팅 컨테이너에 메시지 추가
    chatContainer.appendChild(messageElement);

    // 최신 메시지가 보이도록 스크롤
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
