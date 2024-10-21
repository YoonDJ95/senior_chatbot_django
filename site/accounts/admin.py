from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'phone_number', 'address', 'detailed_address', 'get_business_types')

    # 성과 이름을 가져오는 메서드 추가
    def get_first_name(self, obj):
        return obj.user.first_name  # User 모델의 first_name 필드에 접근

    def get_last_name(self, obj):
        return obj.user.last_name  # User 모델의 last_name 필드에 접근

    # Admin에서 컬럼명 지정
    get_first_name.short_description = '이름'
    get_last_name.short_description = '성'

    # 업종을 보여주는 메서드 추가
    def get_business_types(self, obj):
        # 리스트로 저장된 업종을 ','로 구분된 문자열로 변환하여 보여줌
        return ', '.join(obj.business_types)

    get_business_types.short_description = '업종'