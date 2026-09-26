#!/usr/bin/env python3
"""
separate_vocal_bgm.py
動画ファイルから「声(ボーカル)」と「BGM(伴奏)」を分離するスクリプト。

内部では以下の処理を行う:
  1. ffmpeg で動画から音声(wav)を抽出
  2. Demucs (音源分離AI) でボーカルとそれ以外(BGM)に分離
  3. 結果を指定フォルダに書き出す

必要な準備(初回のみ):
  1. Python 3.9以上をインストール
  2. ffmpeg をインストールして PATH に通す
     - Windows: https://www.gyan.dev/ffmpeg/builds/ からダウンロードしPATH設定
     - Mac: `brew install ffmpeg`
  3. 依存ライブラリをインストール:
     pip install demucs

使い方:
  python separate_vocal_bgm.py 入力動画.mp4
  python separate_vocal_bgm.py 入力動画.mp4 -o 出力フォルダ

出力:
  出力フォルダ/vocals.wav   … 声のみ
  出力フォルダ/bgm.wav      … BGM(声以外の全音)

補足:
  - Demucsの初回実行時、学習済みモデル(数百MB)が自動ダウンロードされます。
    ネット接続が必要です(2回目以降はキャッシュされるので不要)。
  - モデルは既定で `htdemucs` を使用。精度は高いですが処理に少し時間がかかります
    (5分の動画で数分程度、PCスペックに依存)。
  - Demucsは本来 vocals / drums / bass / other の4つに分けますが、
    このスクリプトは drums+bass+other をまとめて「BGM」として1本にまとめます。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def extract_audio(video_path: Path, wav_path: Path) -> None:
    """ffmpegで動画から音声(wav, 44100Hz, ステレオ)を抽出する"""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "2", "-ar", "44100",
        str(wav_path),
    ]
    print(f"[1/3] 音声を抽出中... ({video_path.name})")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpegでの音声抽出に失敗しました。ffmpegが正しくインストールされているか確認してください。")
        print(result.stderr[-1000:])
        sys.exit(1)


def run_demucs(wav_path: Path, work_dir: Path, model: str) -> Path:
    """Demucsでボーカル分離を実行し、出力フォルダのパスを返す"""
    print("[2/3] AIによる音源分離を実行中...(初回はモデルのダウンロードが入ります)")
    cmd = [
        sys.executable, "-m", "demucs",
        "--two-stems", "vocals",
        "-n", model,
        "-o", str(work_dir),
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Demucsの実行に失敗しました。`pip install demucs` が完了しているか確認してください。")
        print(result.stderr[-2000:])
        sys.exit(1)
    return work_dir / model / wav_path.stem


def main():
    parser = argparse.ArgumentParser(description="動画から声とBGMを分離します")
    parser.add_argument("video", help="入力動画ファイル (mp4など)")
    parser.add_argument("-o", "--output", default="separated", help="出力フォルダ (既定: separated)")
    parser.add_argument("--model", default="htdemucs", help="Demucsのモデル名 (既定: htdemucs)")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"動画ファイルが見つかりません: {video_path}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = output_dir / "_work"
    work_dir.mkdir(exist_ok=True)

    raw_wav = work_dir / (video_path.stem + ".wav")
    extract_audio(video_path, raw_wav)

    demucs_out_dir = run_demucs(raw_wav, work_dir, args.model)

    print("[3/3] ファイルを整理中...")
    vocals_src = demucs_out_dir / "vocals.wav"
    bgm_src = demucs_out_dir / "no_vocals.wav"

    vocals_dst = output_dir / "vocals.wav"
    bgm_dst = output_dir / "bgm.wav"
    vocals_dst.write_bytes(vocals_src.read_bytes())
    bgm_dst.write_bytes(bgm_src.read_bytes())

    print("\n完了しました。")
    print(f"  声のみ: {vocals_dst}")
    print(f"  BGMのみ: {bgm_dst}")


if __name__ == "__main__":
    main()
