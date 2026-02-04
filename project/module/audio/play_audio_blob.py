# audio\play_audio_blob.py

import tempfile
import os
from pydub import AudioSegment
from pydub.playback import play

def play_audio_blob(blob_data, extension="mp3"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as temp_file:
        temp_file.write(blob_data)
        temp_file_path = temp_file.name

    try:
        sound = AudioSegment.from_file(temp_file_path, format=extension)
        play(sound)
    except Exception as e:
        print(f"재생 실패: {e}")
    finally:
        os.remove(temp_file_path)  # 임시 파일 삭제