import os
import tempfile

from flask import Flask, render_template, request, jsonify
from pydub import AudioSegment
from pydub.silence import split_on_silence


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auto-segment', methods=['POST'])
def auto_segment_audio():
    # 获取输入参数，并进行一些简单的校验
    input_file = request.files.get('audio_file')
    if not input_file:
        return jsonify({'msg': '请上传音频文件！'})

    output_folder = request.form.get('output_folder', '').strip()

    if not output_folder:
        return jsonify({'msg': '请输入输出文件夹！'})

    if not os.path.isdir(output_folder):
        return jsonify({'msg': '输出文件夹不存在！'})

    # 将输入文件保存为临时文件，并加载音频
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    input_file.save(temp_file.name)
    audio = AudioSegment.from_file(temp_file.name)

    # 切割音频，并只保存长度大于3秒小于10秒的部分
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-45, keep_silence=500)
    results = []
    for i, chunk in enumerate(chunks):
        if 3000 < len(chunk) < 10000:
            chunk_filename = f'chunk_{i}.wav'
            chunk_path = os.path.join(output_folder, chunk_filename)
            chunk.export(chunk_path, format='wav')
            results.append(chunk_filename)

    # 返回处理结果
    return jsonify({'msg': '自动分段完成！', 'results': results})


if __name__ == '__main__':
    app.run(debug=True)
