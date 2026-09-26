# separete_voice_bgm
動画からbgmを取り除いて声だけにできるツールです。有料が多かったので作りました。
# 導入方法
Pythonをインストールしてください。
ffmpegをインストールしてpathを通してください。（Macの場合```brew install ffmpeg```を実行する）
```pip install demucs```を実行してください。
# 使い方
ターミナルで```python separate_vocal_bgm.py 入力動画.mp4```を入力してください。
初回はAIモデル(数百MB)が自動ダウンロードされるのでネット接続が必要です。
処理後separatedフォルダにvocals.wav(声のみ)とbgm.wav(BGMのみ)が出力されます。
