import os
import uuid
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory
from pdf2image import convert_from_bytes
from PIL import Image
from zipfile import ZipFile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 최대 20MB

# 출력 폴더 없으면 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'})

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})

    try:
        # 고유한 디렉토리 생성
        session_id = str(uuid.uuid4())
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(output_dir, exist_ok=True)

        # PDF → 이미지 변환
        images = convert_from_bytes(pdf_file.read(), dpi=200)
        image_paths = []

        for i, img in enumerate(images):
            img_path = os.path.join(output_dir, f'page{i+1}.jpg')
            img.save(img_path, 'JPEG')
            image_paths.append('/' + img_path.replace('\\', '/'))

        # 이미지 압축 (ZIP)
        zip_filename = os.path.join(output_dir, 'converted_images.zip')
        with ZipFile(zip_filename, 'w') as zipf:
            for img_path in image_paths:
                full_path = img_path.lstrip('/')
                zipf.write(full_path, arcname=os.path.basename(full_path))

        return jsonify({
            'success': True,
            'images': image_paths,
            'zip_url': '/' + zip_filename.replace('\\', '/')
        })

    except Exception as e:
        print("변환 에러:", e)
        return jsonify({'success': False, 'message': '서버 에러'})

# 개발 중 static 파일 자동 새로고침 방지 (브라우저 캐시 무시)
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000,debug=True)
