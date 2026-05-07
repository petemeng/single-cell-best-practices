"""Generate a Simplified Chinese copy of the Jupyter Book.

The script copies ``jupyter-book`` to ``jupyter-book-zh`` and translates the
reader-facing Markdown text while preserving executable code, notebook outputs,
citations, links, formulas, and MyST/Sphinx roles as much as possible.

It uses the public Google Translate endpoint by default and stores translations
in a JSON cache so interrupted runs can be resumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - friendly CLI failure
    raise SystemExit("PyYAML is required: python -m pip install PyYAML") from exc


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "jupyter-book"
TARGET_DIR = ROOT / "jupyter-book-zh"
CACHE_PATH = ROOT / ".translation-cache" / "google-en-zh-CN.json"

TRANSLATED_FILE_SUFFIXES = {".md", ".txt", ".ipynb"}
COPY_EXCLUDED_DIRS = {"_build", ".ipynb_checkpoints", "data", "datasets", "archive"}

TITLE_TRANSLATIONS = {
    "Single-cell best practices": "单细胞最佳实践",
    "Introduction": "引言",
    "Preprocessing and visualization": "预处理与可视化",
    "Identifying cellular structure": "识别细胞结构",
    "Inferring trajectories": "推断轨迹",
    "Dealing with conditions": "处理不同条件",
    "Modeling mechanisms": "机制建模",
    "Deconvolution": "去卷积",
    "Chromatin Accessibility": "染色质可及性",
    "Spatial omics": "空间组学",
    "Surface protein": "表面蛋白",
    "Adaptive immune receptor repertoire": "适应性免疫受体库",
    "Multimodal integration": "多模态整合",
    "Outlook": "展望",
    "Acknowledgements": "致谢",
    "Glossary": "术语表",
    "Changelog": "更新日志",
}

TERM_TRANSLATIONS = {
    "best practices": "最佳实践",
    "single-cell": "单细胞",
    "single cell": "单细胞",
    "single-cell RNA sequencing": "单细胞 RNA 测序",
    "single-cell RNA-seq": "单细胞 RNA-seq",
    "scRNA-seq": "scRNA-seq",
    "RNA-seq": "RNA-seq",
    "ATAC-seq": "ATAC-seq",
    "chromatin accessibility": "染色质可及性",
    "spatial transcriptomics": "空间转录组学",
    "multimodal": "多模态",
    "unimodal": "单模态",
    "trajectory": "轨迹",
    "trajectories": "轨迹",
    "pseudotime": "拟时序",
    "RNA velocity": "RNA velocity",
    "cell type": "细胞类型",
    "cell state": "细胞状态",
    "gene expression": "基因表达",
    "quality control": "质量控制",
    "normalization": "归一化",
    "feature selection": "特征选择",
    "dimensionality reduction": "降维",
    "clustering": "聚类",
    "annotation": "注释",
    "integration": "整合",
    "batch correction": "批次校正",
    "doublet detection": "双细胞检测",
    "differential gene expression": "差异基因表达",
    "gene set enrichment analysis": "基因集富集分析",
    "pathway analysis": "通路分析",
    "cell-cell communication": "细胞间通信",
    "gene regulatory network": "基因调控网络",
    "deconvolution": "去卷积",
    "surface protein": "表面蛋白",
    "immune receptor": "免疫受体",
    "clonotype": "克隆型",
    "specificity": "特异性",
    "interoperability": "互操作性",
    "benchmark": "基准测试",
    "benchmarks": "基准测试",
    "review": "综述",
    "reviews": "综述",
    "raw data processing": "原始数据处理",
    "fundamental data structures and frameworks": "基础数据结构与框架",
    "advanced data structures and frameworks": "高级数据结构与框架",
}

PH_RE = re.compile(r"__SCBP_PH_(\d+)__")


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def should_copy_dir(_dir: str, names: list[str]) -> set[str]:
    return {name for name in names if name in COPY_EXCLUDED_DIRS}


def copy_source(force: bool) -> None:
    if TARGET_DIR.exists():
        if not force:
            raise SystemExit(f"{TARGET_DIR} already exists. Use --force to regenerate it.")
        shutil.rmtree(TARGET_DIR)
    shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=should_copy_dir)


class GoogleTranslator:
    def __init__(self, cache_path: Path, sleep_seconds: float = 0.2):
        self.cache_path = cache_path
        self.cache: dict[str, str] = read_json(cache_path, {})
        self.sleep_seconds = sleep_seconds
        self.dirty = False

    @staticmethod
    def key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def translate(self, text: str) -> str:
        if not text.strip():
            return text
        key = self.key(text)
        if key in self.cache:
            return self.cache[key]
        translated = self._request(text)
        self.cache[key] = translated
        self.dirty = True
        if len(self.cache) % 25 == 0:
            self.flush()
        time.sleep(self.sleep_seconds)
        return translated

    def _request(self, text: str) -> str:
        params = urllib.parse.urlencode(
            {
                "client": "gtx",
                "sl": "en",
                "tl": "zh-CN",
                "dt": "t",
                "q": text,
            }
        )
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        last_error: Exception | None = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return "".join(part[0] for part in payload[0] if part and part[0])
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(2**attempt)
        raise RuntimeError(f"Translation failed after retries: {last_error}")

    def flush(self) -> None:
        if self.dirty:
            write_json(self.cache_path, self.cache)
            self.dirty = False


def add_placeholder(placeholders: list[str], value: str) -> str:
    placeholders.append(value)
    return f"__SCBP_PH_{len(placeholders) - 1}__"


def protect(text: str) -> tuple[str, list[str]]:
    placeholders: list[str] = []

    def ph(match: re.Match[str]) -> str:
        return add_placeholder(placeholders, match.group(0))

    patterns = [
        r"```[\s\S]*?```",
        r"\$\$[\s\S]*?\$\$",
        r"(?<!\\)\$[^$\n]+\$",
        r"\\\[[\s\S]*?\\\]",
        r"\\\([^)]+\\\)",
        r"!\[[^\]]*\]\([^)]+\)",
        r"\[[^\]]+\]\([^)]+\)",
        r"\{[A-Za-z0-9_:\-.]+\}`[^`]+`",
        r"\{[A-Za-z0-9_:\-.]+\}",
        r"``[^`]+``",
        r"`[^`]+`",
        r"\{[^{}\n]*\}",
        r"<[^>\n]+>",
        r"https?://[^\s)>\"]+",
        r"www\.[^\s)>\"]+",
        r"\b[A-Za-z0-9_.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        r"\b\d+(?:\.\d+)?\s?(?:%|GB|MB|KB|bp|kb|Mb|Gb|nt|μm|um|µm|mL|µL|ul|s|min|h|x)\b",
        r"\b[A-Za-z0-9_.-]+(?:==|>=|<=|=)\d+(?:\.\d+)*(?:[A-Za-z0-9_.-]*)\b",
        r"\b(?:scRNA-seq|RNA-seq|scATAC-seq|ATAC-seq|CITE-seq|TEA-seq|SHARE-seq|snRNA-seq|scVI|scANVI|Scanpy|AnnData|MuData|Seurat|Bioconductor|Cell Ranger|STARsolo|Salmon|alevin-fry|Kallisto|kb-python|Leiden|Louvain|UMAP|t-SNE|PCA|HVG|KNN|kNN|GEX|ADT|VDJ|AIRR|TCR|BCR|CRISPR|Cas9|DNA|RNA|mRNA|miRNA|UMI|PCR|FASTQ|BAM|SAM|BED|GTF|HDF5|H5AD|H5MU|GPU|CPU)\b",
        r"\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3}\b",
    ]
    protected = text
    for pattern in patterns:
        protected = re.sub(pattern, ph, protected)
    return protected, placeholders


def restore(text: str, placeholders: list[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        index = int(match.group(1))
        return placeholders[index] if index < len(placeholders) else match.group(0)

    previous = None
    restored = text
    for _ in range(20):
        if restored == previous or "__SCBP_PH_" not in restored:
            break
        previous = restored
        restored = PH_RE.sub(repl, restored)
    return restored


def normalize_translation(text: str) -> str:
    text = text.replace("＃", "#")
    text = text.replace("％", "%")

    def fix_heading(match: re.Match[str]) -> str:
        hashes = min(match.group(1).count("#"), 6)
        return "#" * hashes + " " + match.group(2)

    text = re.sub(r"(?m)^((?:#\s*){1,6})([^#\s].*)$", fix_heading, text)
    text = re.sub(r"(?m)^(#{1,6})(?=[^\s#])", r"\1 ", text)
    text = re.sub(r"(?m)^([>*+-])(?=\S)", r"\1 ", text)
    text = re.sub(r"(?m)^(\d+\.)(?=\S)", r"\1 ", text)
    text = re.sub(r"\s+([，。；：？！、])", r"\1", text)
    text = re.sub(r"([（《“])\s+", r"\1", text)
    text = re.sub(r"\s+([）》”])", r"\1", text)
    text = text.replace("` ", "`").replace(" `", "`")
    text = text.replace("{ ", "{").replace(" }", "}")
    return text


def apply_term_overrides(text: str) -> str:
    for english, chinese in sorted(TERM_TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(re.escape(english), flags=re.IGNORECASE)
        text = pattern.sub(chinese, text)
    return text


def should_translate_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped in {"---", "***", "___"}:
        return False
    if stripped.startswith(("```", ":::")):
        return False
    if stripped.startswith(("(", ".. ")):
        return False
    if re.match(r"^\s*[:\-]\w+:", line):
        return False
    if re.match(r"^\s*<[^>]+>\s*$", line):
        return False
    if re.match(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*$", line):
        return False
    return bool(re.search(r"[A-Za-z]{3,}", line))


def translate_inline(text: str, translator: GoogleTranslator, dry_run: bool) -> str:
    leading_ws = re.match(r"^\s*", text).group(0)
    trailing_ws = re.search(r"\s*$", text).group(0)
    protected, placeholders = protect(text)
    translated = protected if dry_run else translator.translate(protected)
    translated = normalize_translation(translated)
    translated = apply_term_overrides(translated)
    translated = restore(translated, placeholders)
    translated = normalize_translation(translated)
    if leading_ws and not translated.startswith(leading_ws):
        translated = leading_ws + translated.lstrip()
    if trailing_ws and not translated.endswith(trailing_ws):
        translated = translated.rstrip() + trailing_ws
    return translated


def split_markdown_blocks(text: str) -> list[tuple[bool, str]]:
    blocks: list[tuple[bool, str]] = []
    buf: list[str] = []
    translatable = True
    fence: str | None = None

    def flush() -> None:
        nonlocal buf
        if buf:
            blocks.append((translatable, "".join(buf)))
            buf = []

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence:
            buf.append(line)
            if stripped.startswith(fence):
                flush()
                fence = None
                translatable = True
            continue
        if stripped.startswith("```"):
            flush()
            translatable = False
            fence = "```"
            buf.append(line)
            continue
        if not line.strip():
            flush()
            blocks.append((False, line))
            continue
        buf.append(line)
    flush()
    return blocks


def translate_markdown(text: str, translator: GoogleTranslator, dry_run: bool = False) -> str:
    out: list[str] = []
    for translatable, block in split_markdown_blocks(text):
        if not translatable:
            out.append(block)
            continue
        lines = block.splitlines(keepends=True)
        if not any(should_translate_line(line) for line in lines):
            out.append(block)
            continue
        if len(block) <= 4500:
            out.append(translate_inline(block, translator, dry_run))
            continue
        translated_lines: list[str] = []
        chunk: list[str] = []
        chunk_size = 0

        def flush_chunk() -> None:
            nonlocal chunk, chunk_size
            if chunk:
                translated_lines.append(translate_inline("".join(chunk), translator, dry_run))
                chunk = []
                chunk_size = 0

        for line in lines:
            if not should_translate_line(line):
                flush_chunk()
                translated_lines.append(line)
                continue
            if chunk_size + len(line) > 4000:
                flush_chunk()
            chunk.append(line)
            chunk_size += len(line)
        flush_chunk()
        out.append("".join(translated_lines))
    return "".join(out)


def translate_text_file(path: Path, translator: GoogleTranslator, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    path.write_text(translate_markdown(text, translator, dry_run), encoding="utf-8")


def translate_notebook(path: Path, translator: GoogleTranslator, dry_run: bool) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        source_text = "".join(source) if isinstance(source, list) else str(source)
        translated = translate_markdown(source_text, translator, dry_run)
        cell["source"] = translated.splitlines(keepends=True) if isinstance(source, list) else translated
        changed = True
    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def update_config_and_toc() -> None:
    config_path = TARGET_DIR / "_config.yml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["title"] = "单细胞最佳实践"
    config["description"] = "单模态与多模态单细胞数据分析教程和指南。"
    config["author"] = "Lukas Heumos, Anna Schaar, single-cell best practices consortium；中文翻译：petemeng"
    config.setdefault("sphinx", {}).setdefault("config", {})["language"] = "zh_CN"
    config["repository"] = {
        "url": "https://github.com/petemeng/single-cell-best-practices",
        "path_to_book": "jupyter-book-zh",
        "branch": "main",
    }
    config.setdefault("html", {})["extra_footer"] = (
        "<div>中文翻译基于 Theislab 与 single-cell community 维护的英文原书。"
        "本译本可能包含机器翻译内容，请以英文原文和原始文献为准。</div>"
    )
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")

    toc_path = TARGET_DIR / "_toc.yml"
    toc = yaml.safe_load(toc_path.read_text(encoding="utf-8"))
    for part in toc.get("parts", []):
        caption = part.get("caption")
        if caption in TITLE_TRANSLATIONS:
            part["caption"] = TITLE_TRANSLATIONS[caption]
        for chapter in part.get("chapters", []):
            title = chapter.get("title")
            if title in TITLE_TRANSLATIONS:
                chapter["title"] = TITLE_TRANSLATIONS[title]
    toc_path.write_text(yaml.safe_dump(toc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def update_readme() -> None:
    (ROOT / "README_zh.md").write_text(
        """# 单细胞最佳实践：中文版本

这个仓库中的 `jupyter-book-zh/` 是基于 upstream `theislab/single-cell-best-practices` 生成的简体中文版本。

## 构建

```bash
jupyter-book build jupyter-book-zh
```

英文原书仍保留在 `jupyter-book/`。中文版本保留原 notebook 的代码单元、输出、图像、引用和数据环境说明，只翻译面向读者的叙述文本。

## 重新生成中文版本

```bash
python scripts/translate_book_zh.py --force
```

翻译缓存保存在 `.translation-cache/`，可用于断点续跑和减少重复请求。机器翻译难免有术语和语气问题，建议后续按章节人工校订，尤其是统计建模、免疫受体库和空间组学章节。

## 许可

原书采用 Apache 2.0 许可。中文译本继承原项目许可，并建议引用原始论文：

> Heumos, L., Schaar, A.C., Lance, C. et al. Best practices for single-cell analysis across modalities. Nat Rev Genet (2023). https://doi.org/10.1038/s41576-023-00586-w
""",
        encoding="utf-8",
    )


def refresh_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        target = path if path.is_absolute() else ROOT / path
        try:
            rel = target.relative_to(TARGET_DIR)
        except ValueError:
            continue
        source = SOURCE_DIR / rel
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def iter_target_files(paths: Iterable[Path] | None = None) -> list[Path]:
    if paths:
        selected = []
        for path in paths:
            p = path if path.is_absolute() else ROOT / path
            if p.is_dir():
                selected.extend(child for child in p.rglob("*") if child.is_file())
            else:
                selected.append(p)
        return [p for p in selected if p.suffix.lower() in TRANSLATED_FILE_SUFFIXES]
    return [p for p in TARGET_DIR.rglob("*") if p.is_file() and p.suffix.lower() in TRANSLATED_FILE_SUFFIXES]


def translate_files(paths: list[Path], translator: GoogleTranslator, dry_run: bool) -> None:
    total = len(paths)
    for i, path in enumerate(paths, start=1):
        rel = path.relative_to(ROOT)
        print(f"[{i}/{total}] {rel}", flush=True)
        if path.suffix.lower() == ".ipynb":
            translate_notebook(path, translator, dry_run)
        else:
            translate_text_file(path, translator, dry_run)
        translator.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Regenerate jupyter-book-zh from jupyter-book.")
    parser.add_argument("--dry-run", action="store_true", help="Copy and rewrite config without calling translation.")
    parser.add_argument("--refresh-paths", action="store_true", help="Refresh selected target paths from jupyter-book before translating them.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between uncached translation calls.")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional target paths to translate after copy.")
    args = parser.parse_args()

    if not TARGET_DIR.exists() or args.force:
        copy_source(force=args.force)
    update_config_and_toc()
    update_readme()
    if args.refresh_paths and args.paths:
        refresh_paths(args.paths)

    translator = GoogleTranslator(CACHE_PATH, sleep_seconds=args.sleep)
    paths = iter_target_files(args.paths)
    translate_files(paths, translator, dry_run=args.dry_run)
    translator.flush()


if __name__ == "__main__":
    main()
