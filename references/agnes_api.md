# Agnes 接口速查 + 双参考实测结论

## 工具位置
- 脚本：零依赖 Python 脚本，直接打官方接口（见本仓库 `scripts/` 或自行封装）
- 输出目录：`./output/`（本地任意路径）

## 动作清单（脚本封装）
| 动作 | 用途 | 关键参数 |
|---|---|---|
| `image` | 文生图（出资产/分镜故事版） | `--prompt` `--size` `--n` |
| `edit` | 图生图（视角变换，**不可靠**） | `--images` |
| `video` | 文生视频 | `--prompt` `--seconds 5/10/18` |
| `video-img` | 图生视频（**双参考核心**） | `--image`(主) `--extra-images`(多) `--seconds` |

## 视频字段（实测 2026-09-19）
- `POST /videos` 发：`model=agnes-video-v2.0, prompt, width, height, num_frames, frame_rate`
- **单图**：`image`（base64 data URI）
- **多参考图**：`images`（base64 列表）—— 实测 HTTP 200 接受，任务正常创建。
  → 这是「画布式人物节点+场景节点同时连线」的本地实现，**双参考锁一致性治换脸**。
- 异步：提交后轮询 `GET /videos/{id}`，`status=completed` 后视频地址在**响应顶层 `url`** 字段。
- 帧数映射：5s=121帧、10s=241帧、18s=441帧（24fps）。

## 关键坑（务必记住）
1. **免费档并发限流 429** `rate_limit_exceeded` → 多段视频**必须串行**，前段完成再提后段。
2. **5s 短镜头最稳**，18s 长镜头易崩、易超时。品牌种草片统一用 5s。
3. **品牌字/logo 让 Agnes 生成必出乱码**（实测黑袋出 "KAKIN" 乱码）→ 袋写「素面不写字」，logo 剪映后期贴。
4. **imageio 整段 load 121帧 mp4 爆内存（313MiB OOM）** → 抽帧用 `extract_tail.py`（ffmpeg `-ss` 抽单帧）。
5. **edit 接口视角变换报 500**（`could not convert string to float`）→ 不依赖 edit，用「定妆正脸双参考」锁人。
6. 尺寸 `1024x1024`、`1024x1792`(9:16)、`1792x1024`(16:9) 均实测可用。
7. 沙箱内 curl 走代理报 `upstream connect failed` 时加 `--noproxy '*'`（脚本内 urllib 不受影响）。

## 音频 / 配音（必知）
- **Agnes 视频模型 `agnes-video-v2.0` 是纯视觉生成，不带 TTS**：它出"画面 + 口型"，声音需单独生成再对轨（剪映 TTS 或独立 TTS），详见 `prompt_templates.md` 模板8 与 `prompt_methodology.md` 的「音频设计」维度。
- 配音去假三法：标点控语气 + 情绪翻译成发声方式 + 真实情境入场（台词要带标点、情绪写具体发声指令、开场铺情境）。

## 双参考锁一致性（本工作流灵魂）
```
每个镜头都喂：--image 定妆正脸图  --extra-images 场景定稿图
+ 提示词锁脸句「画面主角是参考图中同一位…五官脸型发型不变」
+ 提示词锁背景句「背景干净无人，仅主角一人」
+ 固定机位（不横移/跟随）
→ 治换脸 + 治乱穿插，且不靠尾帧无限接力（避免误差累加）。
每 2-3 段重新喂一次定妆脸回血。
```
