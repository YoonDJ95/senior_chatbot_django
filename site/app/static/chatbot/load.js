var mapWrapper = document.getElementById('mapWrapper'); // 지도를 감싸고 있는 DIV 태그

// 전역 변수로 선언하여 다른 파일에서 접근 가능하게 함
var map, rv, rvMarker, handleSelectButtonClick;

// 지도 초기화
var mapContainer = document.getElementById('map'), // 지도를 표시할 div
    mapCenter = new kakao.maps.LatLng(33.450422139819736, 126.5709139924533), // 기본 중심 좌표
    mapOption = {
        center: mapCenter, // 지도의 중심좌표
        level: 4 // 지도의 확대 레벨
    };

// 지도 생성
map = new kakao.maps.Map(mapContainer, mapOption);

// 로드뷰 컨테이너 및 로드뷰 객체 생성
var rvContainer = document.getElementById('roadview');
rv = new kakao.maps.Roadview(rvContainer);
var rvClient = new kakao.maps.RoadviewClient(); // 로드뷰 좌표 가져올 helper

// 마커 이미지 생성
var markImage = new kakao.maps.MarkerImage(
    'https://t1.daumcdn.net/localimg/localimages/07/2018/pc/roadview_minimap_wk_2018.png',
    new kakao.maps.Size(26, 46),
    {
        spriteSize: new kakao.maps.Size(1666, 168),
        spriteOrigin: new kakao.maps.Point(705, 114),
        offset: new kakao.maps.Point(13, 46)
    }
);

// 드래그 가능한 마커 생성
rvMarker = new kakao.maps.Marker({
    image: markImage,
    position: mapCenter,
    draggable: true,
    map: map
});

// 마커 드래그 종료 시 로드뷰 및 지도 업데이트
kakao.maps.event.addListener(rvMarker, 'dragend', function(mouseEvent) {
    var position = rvMarker.getPosition(); // 마커가 놓인 자리의 좌표
    toggleRoadview(position); // 로드뷰 업데이트
});

// 지도 클릭 시 마커 및 로드뷰 업데이트
kakao.maps.event.addListener(map, 'click', function(mouseEvent) {
    var position = mouseEvent.latLng; // 클릭한 좌표
    rvMarker.setPosition(position); // 마커 위치 변경
    toggleRoadview(position); // 로드뷰 업데이트
});

// 선택 버튼 클릭 시 지도를 해당 좌표로 이동시키는 함수
handleSelectButtonClick = function(lat, lng) {
    console.log(`수신받음 지도 이동: ${lat}, ${lng}`);
    var newCenter = new kakao.maps.LatLng(lat, lng); // 새로운 중심 좌표 생성

    // 지도 중심 이동
    map.setCenter(newCenter);

    // 마커 위치 이동
    rvMarker.setPosition(newCenter);

    // 로드뷰 업데이트
    toggleRoadview(newCenter);
}

// 로드뷰 업데이트 함수
function toggleRoadview(position) {
    rvClient.getNearestPanoId(position, 50, function(panoId) {
        if (panoId === null) {
            //rvContainer.style.display = 'none'; // 로드뷰 숨기기
            //mapWrapper.style.width = '100%';
            map.relayout();
        } else {
            //mapWrapper.style.width = '50%';
            map.relayout(); // 지도의 레이아웃을 재정렬
            //rvContainer.style.display = 'block'; // 로드뷰 표시
            rv.setPanoId(panoId, position); // 로드뷰 설정
            rv.relayout(); // 로드뷰 레이아웃 재정렬
        }
    });
}

// 초기 로드뷰 설정
toggleRoadview(mapCenter);
