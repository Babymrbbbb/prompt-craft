# -*- coding: utf-8 -*-
"""截取视频尾帧（用于尾帧接力或质检）。零依赖，优先 imageio，内存不足自动回退 ffmpeg 抽单帧。
用法: python extract_tail.py <video.mp4> <out.png>
坑: imageio 整段 load 121帧 mp4 会吃 ~300MB 内存（OOM 时报
    "Unable to allocate 313. MiB"）；ffmpeg -ss 抽单帧最省。
"""
import sys, os, subprocess

def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def last_frame(video, out_png):
    # 优先 ffmpeg 抽最后一帧（最省内存）
    ff = _ffmpeg()
    r = subprocess.run([ff, "-y", "-sseof", "-0.2", "-i", video,
                        "-frames:v", "1", out_png], capture_output=True)
    if r.returncode == 0 and os.path.exists(out_png):
        return "ffmpeg"
    # 回退 imageio（需 pip install imageio imageio-ffmpeg）
    try:
        import imageio.v3 as iio
        import PIL.Image as I
        frames = list(iio.imread(video))
        I.fromarray(frames[-1]).save(out_png)
        return "imageio"
    except Exception as e:
        raise SystemExit("尾帧提取失败: %s" % e)

if __name__ == "__main__":
    video, out_png = sys.argv[1], sys.argv[2]
    src = last_frame(video, out_png)
    print("TAIL_FRAME src=%s out=%s" % (src, out_png))
