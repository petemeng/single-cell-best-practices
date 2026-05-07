# 单细胞最佳实践：中文版本

这个仓库中的 `jupyter-book-zh/` 是基于 upstream `theislab/single-cell-best-practices` 生成的简体中文版本。

英文原书仍保留在 `jupyter-book/`。中文版本保留原 notebook 的代码单元、输出、图像、引用和数据环境说明，只翻译面向读者的叙述文本。

## 构建

```bash
jupyter-book build jupyter-book-zh
```

如果没有本地 Jupyter Book 环境，也可以使用临时工具环境：

```bash
uv tool run --from jupyter-book==1.0.4.post1 --with jupytext==1.16.7 --with beautifulsoup4==4.13.3 --with sphinx==7.4.7 jupyter-book build jupyter-book-zh
```

构建完成后，入口页面在：

```text
jupyter-book-zh/_build/html/index.html
```

## 以后同步英文原书更新

本仓库已经配置了两个远程：

- `origin`：你的 fork，`petemeng/single-cell-best-practices`
- `upstream`：原作者仓库，`theislab/single-cell-best-practices`

推荐流程：

1. 先提交当前中文版本，保证工作区干净。
2. 运行更新脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/update_from_upstream_zh.ps1
```

脚本会执行这些动作：

1. 从 `upstream/main` 拉取英文原书更新。
2. 合并到你的当前分支。
3. 使用 `scripts/translate_book_zh.py --force` 重新生成 `jupyter-book-zh/`。
4. 使用 Jupyter Book 构建中文 HTML 做验证。
5. 显示 Git 状态，方便你检查、提交、推送。

如果只想更新中文源文件，暂时不构建网页：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/update_from_upstream_zh.ps1 -SkipBuild
```

## 翻译缓存

翻译缓存保存在 `.translation-cache/`。它很重要：后续英文原书小幅更新时，已翻译过的段落会直接复用缓存，只翻译新增或变化的片段。

建议保留并提交这个缓存文件，这样在另一台机器上也能继续增量更新。

## 人工校订建议

这是一版机器翻译初稿，难免有术语、语气和句法问题。建议后续按章节人工校订，尤其是：

- 统计建模和差异分析章节
- 免疫受体库章节
- 空间组学章节
- 轨迹推断和 RNA velocity 章节

人工校订时可以直接改 `jupyter-book-zh/`。不过要注意：再次运行 `translate_book_zh.py --force` 会重新生成中文目录，覆盖人工改动。比较稳的做法是把人工校订内容也回写到翻译缓存或维护成单独补丁。

## 许可

原书采用 Apache 2.0 许可。中文译本继承原项目许可，并建议引用原始论文：

> Heumos, L., Schaar, A.C., Lance, C. et al. Best practices for single-cell analysis across modalities. Nat Rev Genet (2023). https://doi.org/10.1038/s41576-023-00586-w
