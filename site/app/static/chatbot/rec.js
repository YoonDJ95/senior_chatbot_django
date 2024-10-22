document.addEventListener('DOMContentLoaded', function () {
    const startRecordingButton = document.getElementById('recordingButton');  // 버튼을 찾음
    const userAddressElement = document.getElementById('userAddress');  // 인식된 텍스트를 출력할 필드

    if (!startRecordingButton || !userAddressElement) {
        console.error("필수 HTML 요소가 존재하지 않습니다.");
        return;  // 요소가 없으면 나머지 코드 실행 중지
    }

    let recognition;
    let isRecognizing = false;

    // Web Speech API 설정
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
    } else if ('SpeechRecognition' in window) {
        recognition = new SpeechRecognition();
    } else {
        console.error('이 브라우저는 Web Speech API를 지원하지 않습니다.');
        alert('Web Speech API를 지원하지 않는 브라우저입니다.');
        return;
    }

    if (recognition) {
        recognition.lang = 'ko-KR';  // 한국어로 설정
        recognition.continuous = false;  // 한 번에 한 문장만 인식
        recognition.interimResults = false;  // 중간 결과 표시 안함

        recognition.onstart = function () {
            isRecognizing = true;
            startRecordingButton.textContent = '녹음중';  // 녹음중으로 텍스트 변경
            startRecordingButton.style.backgroundColor = '#808080';  // 배경색을 회색으로 변경
            console.log('음성 인식 시작');
        };

        recognition.onend = function () {
            isRecognizing = false;
            startRecordingButton.textContent = '녹음하기';  // 다시 녹음하기로 변경
            startRecordingButton.style.backgroundColor = '';  // 원래 색상으로 복귀 (기본값)
            console.log('음성 인식 종료');
        };

        // 음성 인식 결과 처리
        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            console.log('인식된 텍스트:', transcript);

            // 인식된 텍스트를 userAddress 필드에 출력
            userAddressElement.value = transcript;

            // 서버로 텍스트 전송 (필요 시)
            fetch('/save_transcript/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()  // CSRF 토큰 설정
                },
                body: JSON.stringify({ recognized_text: transcript })
            }).then(response => response.json())
              .then(data => console.log('서버 응답:', data))
              .catch(error => console.error('서버 전송 중 오류:', error));
        };

        recognition.onerror = function (event) {
            console.error('음성 인식 오류:', event.error);
        };

        // 버튼 클릭 시 음성 인식 시작/중지
        startRecordingButton.addEventListener('click', function () {
            if (isRecognizing) {
                recognition.stop();  // 인식 중이면 중지
            } else {
                recognition.start();  // 인식 시작
            }
        });
    }

    // CSRF 토큰을 가져오는 함수
    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
