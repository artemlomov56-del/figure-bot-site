from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'videos'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs('videos', exist_ok=True)

PHONE_NUMBER = '+79262019202'
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'queue': [], 'next_id': 1}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html', phone=PHONE_NUMBER)

@app.route('/submit', methods=['POST'])
def submit_video():
    data = load_data()
    name = request.form.get('name', 'Аноним')
    contact = request.form.get('contact', '')
    element = request.form.get('element', '')
    
    if 'video' not in request.files:
        return jsonify({'error': 'Нет видео'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    filename = secure_filename(f"{data['next_id']}_{video.filename}")
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(video_path)
    
    new_entry = {
        'id': data['next_id'],
        'name': name,
        'contact': contact,
        'element': element,
        'video_file': filename,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    data['queue'].append(new_entry)
    data['next_id'] += 1
    save_data(data)
    
    return jsonify({
        'success': True,
        'position': len(data['queue']),
        'id': new_entry['id']
    })

@app.route('/admin')
def admin():
    data = load_data()
    return render_template('admin.html', queue=data['queue'])

@app.route('/admin/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    data = load_data()
    data['queue'] = [e for e in data['queue'] if e['id'] != entry_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/videos/<filename>')
def videos(filename):
    return send_from_directory('videos', filename)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("✅ САЙТ ЗАПУЩЕН!")
    print(f"📱 Открой в браузере: http://localhost:{port}")
    print(f"🔐 Админка: http://localhost:{port}/admin")
    app.run(host='0.0.0.0', port=port)
