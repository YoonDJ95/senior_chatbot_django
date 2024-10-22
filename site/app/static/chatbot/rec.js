document.addEventListener('DOMContentLoaded', function () {
    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];  // 녹음된 오디오 데이터를 저장할 배열

    const toggleRecordingButton = document.getElementById('recordingButton');
    const userAddressElement = document.getElementById('userAddress');

    if (!userAddressElement) {
        console.error('userAddress 요소를 찾을 수 없습니다.');
        return;
    }

    // 녹음 시작/중지 버튼 클릭 시 실행
    toggleRecordingButton.addEventListener('click', function () {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    // 녹음 시작 함수
    function startRecording() {
        console.log("녹음 시작 중...");
        audioChunks = [];  // 이전 녹음 데이터 초기화
        userAddressElement.value = "";  // 기존 텍스트 지우기

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                isRecording = true;

                console.log("녹음이 시작되었습니다.");
                toggleRecordingButton.textContent = "녹음 중";
                toggleRecordingButton.classList.add("recording");

                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener('stop', () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    console.log("녹음이 중지되었습니다. 오디오 데이터를 서버로 전송 중...");

                    sendAudioToServer(audioBlob);
                    toggleRecordingButton.textContent = "녹음하기";
                    toggleRecordingButton.classList.remove("recording");
                });
            })
            .catch(error => {
                console.error('마이크 접근 중 오류 발생:', error);
            });
    }

    // 녹음 중지 함수
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            console.log("녹음이 중지되었습니다.");
        } else {
            console.log("녹음 중지 요청 시점에 녹음이 진행 중이지 않았습니다.");
        }
    }

    // 서버로 오디오 데이터를 전송하는 함수
    function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        console.log("서버로 오디오 데이터를 보내는 중...");

        fetch(toggleRecordingUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    console.error('서버 응답 실패:', response.statusText);
                    throw new Error('서버 응답 실패');
                }
                return response.json();
            })
            .then(data => {
                if (data.recognized_text) {
                    console.log("서버 응답 데이터:", data.recognized_text);
                    userAddressElement.value = data.recognized_text;
                } else if (data.error) {
                    console.error("서버 오류 응답:", data.error);
                    userAddressElement.value = "인식 오류: " + data.error;
                } else {
                    console.error("서버 응답 데이터가 없습니다.");
                    userAddressElement.value = "텍스트 인식에 실패했습니다.";
                }
            })
            .catch(error => {
                console.error('오디오 전송 중 오류 발생:', error);
                userAddressElement.value = "서버 오류 발생: " + error.message;
            });
    }

    // CSRF 토큰 가져오는 함수
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
