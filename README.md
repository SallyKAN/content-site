# 内容站

自动生成的静态内容站，部署于 Cloudflare Pages。

## 专栏
- 🧰 每日独立开发精选 — Hacker News / Product Hunt / Reddit / SomebodyMakeThis
- ✍️ 选题日报 — AI 热点选题方案与晚间推送

## 构建
```bash
python3 build.py
```
输出到 `output/`。

## 加新专栏
编辑 `build.py` 顶部的 `SOURCES` 列表即可，无需改渲染逻辑。
