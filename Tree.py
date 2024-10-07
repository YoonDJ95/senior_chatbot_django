import os

# 생략할 폴더 목록
excluded_folders = ['__pycache__', '.git', 'node_modules','migrations','mysite','ad','chromedriver-win64','.vscode','.gitattributes','.gitignore','notice,py','Tree.py',
                    '__init__.py','apps.py','tests.py','asgi.py','wsgi.py'
                    ]

def print_directory_tree(startpath, indent=""):
    for item in os.listdir(startpath):
        item_path = os.path.join(startpath, item)

        # 생략할 폴더라면 스킵
        if item in excluded_folders:
            continue

        # 출력
        print(indent + "|-- " + item)

        # 하위 폴더에 대해 재귀 호출 (폴더만 처리)
        if os.path.isdir(item_path):
            print_directory_tree(item_path, indent + "|   ")

# 사용할 경로 설정
directory_path = "C:\go"
print_directory_tree(directory_path)

