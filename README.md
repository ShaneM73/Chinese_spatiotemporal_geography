# 中国时空地理 · Chinese Spatiotemporal Geography

中国及周边地区的交互式三维**时空立方体**，范围西起帕米尔与塔里木盆地，东至日本列岛，北抵贝加尔湖与黑龙江，南达越南中部与暹罗湾。地形图展示某一时刻的政权疆域，并沿纵向时间轴在公元前2000年至2010年之间滑动，穿过48个历史快照逐层堆叠的疆界。227个历史事件按发生的地点和时间置于立方体中。

An interactive 3D **space–time cube** of China and its neighbours, from the Pamirs and the Tarim Basin to Japan, and from Lake Baikal and the Amur to central Vietnam. A relief map shows political boundaries at a chosen moment and slides along a vertical time axis from 2000 BCE to 2010, through the stacked boundary layers of 48 historical snapshots. 227 historic events sit in the cube at their place and time. It is built the same way as [European_spatiotemporal_geography](https://github.com/ShaneM73/European_spatiotemporal_geography).

## 功能 · Features

- **时空立方体**：x/y 为地图（以中国为中心的等积投影），z 为时间。每个快照的疆界沿时间轴叠放，离当前年份越远越淡。
- **三维地形切片**：所选年份绘制在地貌晕渲图上，垂直夸张可调。
- **追踪政权**：点击某个政权，突出显示它在各个快照中的疆域，形成一条贯穿时间的柱体。
- **历史事件**：◆ 标记战役、条约、宗教与文化事件以及灾害，从二里头、牧野之战到北京奥运。点击可查看简介、当时的疆域及维基百科链接（按读者语言打开对应条目）。
- **视图**：立方体、地图（俯视）、侧视（时间纵向）。时间轴可按年份比例，或按快照等间距排列。
- **地名**：144个地名（海洋、河流、山脉、高原、沙漠与城市），城市按时代显示当时的名称（镐京 → 长安 → 西安；蓟 → 幽州 → 燕京 → 中都 → 大都 → 北平 → 北京；江户 → 东京；升龙 → 河内）。定义见 `data/places.json`。
- **四种语言**：简体中文（基础语言）、繁體中文、English、日本語。界面、时期、事件简介、地名和全部322个政权名称均已翻译。语言根据浏览器自动选择，可记忆，也可用 `#lang=ja` 分享。
- 时间轴拖动、播放、键盘控制（← → 切换，空格播放，Esc 取消），浅色与深色主题，可分享链接（`#year=1279`）。

- **时段聚焦（时间透镜）**：将四个时期在时间轴上放大——三国（184—280年）、五胡乱华（300—439年）、抗日战争（1931—1945年）、国共内战（1945—1950年）。时段内的事件按月或按日展开，一条连线按时间顺序串起它们。半透明的割据疆域层悬浮在各自的年份：三国有曹魏、蜀汉、东吴、袁绍和西晋七个阶段，五胡乱华有汉赵／后赵、诸燕、前后秦、河西诸凉、成汉、北魏与东晋南朝六个阶段，抗日战争有日军占领区六个阶段，国共内战有中共与国民政府控制区六个阶段。没有开放许可的逐年疆域数据，因此 `tools/build_war_layers.py` 用基础快照的轮廓和手绘区域合成这些图层，均为近似。时段打开后，每个阶段和事件都成为时间轴上的一站，可拖动、用方向键或播放逐步查看，地图切片会以斜线显示当时的割据范围。点击图例颜色可单独显示或隐藏某一方。

Focus bands (time lenses), as in the European atlas: the Three Kingdoms (184–280), the Sixteen Kingdoms (300–439), the War of Resistance against Japan (1931–1945) and the Civil War (1945–1950). Each stretches its period along the time axis, with approximate territory phases built by `tools/build_war_layers.py` and the period's dated events as timeline stops.

## 本地运行 · Running locally

静态网站，但必须通过 HTTP 访问（不能直接打开文件）：

```bash
python -m http.server 8000
```

然后打开 <http://localhost:8000>。

## 数据 · Data

| 图层 Layer | 来源 Source | 许可 Licence |
|---|---|---|
| 历史疆域 Historical boundaries | [aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps) | GPL-3.0 |
| 历史事件 Historic events | `data/events.json`，自编简介并链接维基百科 | — |
| 高程 Elevation | [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/)（Mapzen；SRTM、GMTED2010、ETOPO1 等） | 见 [attribution](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) |

`data/boundaries.json` 和 `data/terrain.png` 由 `tools/build_data.py` 生成。该脚本：

- 将每个快照裁剪到东亚范围；
- 重投影为兰伯特方位等积投影（lon₀ 108°，lat₀ 36°）；
- 将疆界简化到约 2.5 公里，并去掉小于 40 平方公里的碎片；
- 为每个统治者（`SUBJECTO`）在所有时代分配同一种颜色，并让相邻政权颜色不同；
- 将地形重采样为 5 公里网格，海陆掩膜取自 2010 年海岸线。

原始数据中东亚部分的若干错误在构建时修正（只改名称，疆界不变）：公元前1500年的“Zhoa”改为商、前1000年和前700年改为周；500年的“晋”改为南齐；700年的“隋”改为唐；1200年的“辽”改为金；1700年的南明残余并入清；1914年改为中华民国；1960年西藏并入中国。1400年的快照沿用了1300年的元朝疆域，脚本用1492年的明朝和朝鲜疆域将其切分为明、朝鲜和北元。

Historical borders are approximate, especially before the Common Era, and each snapshot is shown until the next one. The build fixes the source's clearest East Asian errors (names only, plus the 1400 split described above); other inaccuracies in the source remain.

翻译文件位于 `data/i18n/<lang>.json`，以 `zh-CN.json` 为基础。添加语言时，复制 `zh-CN.json`，翻译其值（保留键名和 `{占位符}`），加入事件翻译（`events`，以事件的 `wiki` 键为键），并将语言代码加入 `js/app.js` 的 `LANGUAGES`。`tools/fetch_wiki_links.py` 用于更新 `data/events.json` 中各语言的维基百科条目名。

重新生成数据（需要 `numpy`、`pillow`、`shapely`）：

```bash
python tools/build_data.py --raw path/to/download-cache
```

## 许可 · Licence

[GPL-3.0](LICENSE)，与其所依据的 historical-basemaps 疆域数据一致。

## 技术栈 · Stack

[three.js](https://threejs.org) r169（从 jsDelivr 加载），原生 ES 模块，无需构建。
