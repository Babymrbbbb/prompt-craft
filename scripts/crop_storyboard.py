# -*- coding: utf-8 -*-
"""裁切九宫格分镜故事版为单格图（用于逐格图生视频）。
用法: python crop_storyboard.py <storyboard.png> <out_dir> [rows=3] [cols=3]
说明: 按 rows x cols 均分裁切，文件名带序号+网格位置。零依赖(PIL)。
"""
import sys, os
from PIL import Image

def main():
    if len(sys.argv) < 3:
        raise SystemExit("用法: python crop_storyboard.py <storyboard.png> <out_dir> [rows] [cols]")
    src, out = sys.argv[1], sys.argv[2]
    rows = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    os.makedirs(out, exist_ok=True)
    im = Image.open(src)
    w, h = im.size
    cw, ch = w // cols, h // rows
    for r in range(rows):
        for c in range(cols):
            box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
            idx = r * cols + c + 1
            p = os.path.join(out, "cell_%02d.png" % idx)
            im.crop(box).save(p)
            print("cell_%02d  grid(%d,%d)  %s" % (idx, r, c, p))
    print("done: %dx%d grid from %s" % (rows, cols, src))

if __name__ == "__main__":
    main()
