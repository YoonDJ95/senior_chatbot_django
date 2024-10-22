document.addEventListener('DOMContentLoaded', function () {
    const recordingButtons = document.querySelectorAll('.recordingButton');  // 모든 녹음 버튼을 선택

    let recognition;
    let isRecognizing = false;
    let activeButton = null;

    // Web Speech API 지원 여부 확인
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
    } else if ('SpeechRecognition' in window) {
        recognition = new SpeechRecognition();
    } else {
        console.error('이 브라우저는 Web Speech API를 지원하지 않습니다.');
        alert('Web Speech API를 지원하지 않는 브라우저입니다.');
        return;
    }

    recognition.continuous = false;  // 한 번에 한 문장만 인식
    recognition.interimResults = false;  // 중간 결과 표시 안함

    // 녹음 버튼에 대해 각각 이벤트 리스너를 설정
    recordingButtons.forEach(button => {
        button.addEventListener('click', function () {
            const lang = button.getAttribute('data-lang');  // 버튼의 언어 설정
            const targetId = button.getAttribute('data-target');  // 텍스트를 출력할 필드의 ID
            const type = button.getAttribute('data-type');  // 버튼이 숫자 인식을 위한 것인지 확인
            const targetInput = document.getElementById(targetId);

            if (!targetInput) {
                console.error(`ID가 ${targetId}인 텍스트 필드를 찾을 수 없습니다.`);
                return;
            }

            if (isRecognizing) {
                recognition.stop();  // 이미 인식 중이면 중지
                button.textContent = '🎤';  // 녹음 버튼 원래 상태로
                button.style.backgroundColor = '';
            } else {
                recognition.lang = lang;  // 버튼에 설정된 언어로 음성 인식
                recognition.start();
                button.textContent = '🎤 녹음중...';
                button.style.backgroundColor = '#808080';  // 녹음 중일 때 버튼 색상 변경
                activeButton = button;
            }

            // 음성 인식 시작 시
            recognition.onstart = function () {
                isRecognizing = true;
                console.log('음성 인식 시작');
            };

            // 음성 인식 종료 시
            recognition.onend = function () {
                isRecognizing = false;
                if (activeButton) {
                    activeButton.textContent = '🎤';
                    activeButton.style.backgroundColor = '';
                }
                console.log('음성 인식 종료');
            };

            // 음성 인식 결과 처리
            recognition.onresult = function (event) {
                let transcript = event.results[0][0].transcript;

                // 숫자만 추출하는 경우
                if (type === 'numeric') {
                    transcript = transcript.replace(/[^0-9]/g, '');  // 숫자 외의 문자는 제거
                }

                targetInput.value = transcript;  // 인식된 텍스트를 해당 필드에 출력
            };

            recognition.onerror = function (event) {
                console.error('음성 인식 오류:', event.error);
            };
        });
    });
});


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
