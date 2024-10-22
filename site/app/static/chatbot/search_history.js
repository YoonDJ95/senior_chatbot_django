function toggleResults(element) {
    const resultsDiv = element.querySelector('.results');
    if (resultsDiv.style.display === 'none' || resultsDiv.style.display === '') {
        resultsDiv.style.display = 'block'; // 결과 보이기
    } else {
        resultsDiv.style.display = 'none'; // 결과 숨기기
    }
}

function clearSearchHistory() {
    if (confirm('검색 기록을 정말로 지우시겠습니까?')) {
        // AJAX 요청으로 서버에 기록 지우기 요청
        fetch('/clear-search-history/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // CSRF 토큰 추가
            }
        })
        .then(response => {
            if (response.ok) {
                alert('검색 기록이 성공적으로 지워졌습니다.');
                location.reload(); // 페이지 새로고침
            } else {
                alert('검색 기록을 지우는 데 오류가 발생했습니다.');
            }
        })
        .catch(error => {
            console.error('오류:', error);
            alert('검색 기록을 지우는 데 문제가 발생했습니다.');
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
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