(raw-proc)=

# 原始数据处理

(introduction-raw-data-processing-key-takeaway-1)=

## 动机

单细胞 {term}`sequencing`中的原始数据处理将测序机输出（所谓的泳道解复用 {term}`FASTQ`文件）转换为易于分析的表示形式，例如计数矩阵。
该矩阵表示每个量化细胞中每个基因衍生的不同分子的估计数量，有时按每个分子的推断剪接状态进行分类 ({numref}`raw-proc-fig-overview`)。

:::{figure-md} raw-proc-fig-overview
<img src="../_static/images/raw_data_processing/overview_raw_data_processing.jpg" alt="Chapter Overview" class="bg-primary mb-1" width="800px">

本章讨论主题的概述。图中，“txome”代表转录组。
:::

计数矩阵是各种 scRNA-seq 分析 {cite}`Zappia2021_raw`的基础，包括细胞类型识别或发育轨迹推断。
稳健且准确的计数矩阵对于可靠的 {term}`downstream analyses <Downstream analysis>`至关重要。
此阶段的错误可能会导致基于错过的见解或数据中扭曲信号的无效结论和发现。
尽管输入（FASTQ 文件）和所需的输出（计数矩阵）具有简单的性质，但原始数据处理提出了一些技术挑战。

在本节中，我们重点关注原始数据处理的关键步骤：

1. 读取对齐/映射
2. 细胞条形码（CB）识别与校正
3. 通过{term}`unique molecular identifiers (UMIs) <Unique Molecular Identifier (UMI)>`估计分子计数

我们还讨论了每个步骤中涉及的挑战和权衡。

```{admonition} A note on preceding steps

The starting point for raw data processing is somewhat arbitrary. For this discussion, we treat lane-demultiplexed FASTQ files as the _raw_ input.
However, these files are derived from earlier steps, such as base calling and base quality estimation, which can influence downstream processing.
For example, base-calling errors and index hopping {cite}`farouni2020model` can introduce inaccuracies in FASTQ data.
These issues can be mitigated with computational approaches {cite}`farouni2020model` or experimental enhancements like [dual indexing](https://www.10xgenomics.com/blog/sequence-with-confidence-understand-index-hopping-and-how-to-resolve-it).

Here, we do not delve into the upstream processes, but consider the FASTQ files, derived from, e.g., BCL files via [appropriate tools](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/bcl2fastq-direct), as the raw input under consideration.
```

## 原始数据质量控制

获得原始 FASTQ 文件后，评估测序读数的质量非常重要。
执行此操作的一种快速有效的方法是使用`FastQC`等质量控制 (QC) 工具。
`FastQC`为每个 FASTQ 文件生成详细报告，总结关键指标，例如质量分数、基础内容和其他统计数据，帮助识别文库制备或测序中出现的潜在问题。

虽然许多现代单细胞数据处理工具包括一些内置的质量检查，例如评估序列的 N 含量或映射读数的分数，但运行独立的 QC 检查仍然是良好的做法。

对于对典型`FastQC`报告感兴趣的读者，在以下切换内容中，使用`FastQC`[manual webpage](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) 提供的 [high-quality](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/good_sequence_short_fastqc.html) 和 [low-quality](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/bad_sequence_fastqc.html) Illumina 数据的示例报告，以及 [the RTSF at MSU](https://rtsf.natsci.msu.edu/genomics/technical-documents/fastqc-tutorial-and-faq.aspx)、[the HBC training program](https://hbctraining.github.io/Intro-to-rnaseq-hpc-salmon/lessons/qc_fastqc_assessment.html) 和 [the QC Fail website](https://sequencing.qcfail.com/software/fastqc/) 的教程和说明进行演示`FastQC`报告中的模块。
尽管这些教程不是明确针对单细胞数据制作的，但许多结果仍然与单细胞数据相关，但有一些注意事项如下所述。

在切换部分中，除特别提及外，所有图表均取自`FastQC`[manual webpage](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) 上的示例报告。

值得注意的是，FastQC 报告中的许多 QC 指标仅对生物读数（源自基因转录本的读数）最有意义。
对于单细胞数据集，例如 10x Chromium v​​2 和 v3，这通常对应于 read 2（文件名中包含`R2`的文件），其中包含转录本衍生的序列。
相反，包含条形码和 UMI 序列的技术读数通常不表现出生物学上典型的序列或 GC 内容。
然而，某些指标（例如`N`碱基检出的比例）仍然与所有读取相关。

```{dropdown} Example FastQC Reports and Tutorials

**0. Summary**

The summary panel on the left side of the HTML report displays the module names along with symbols that provide a quick assessment of the module results.
However, `FastQC` applies uniform thresholds across all sequencing platforms and biological materials.
As a result, warnings (orange exclamation marks) or failures (red crosses) may appear for high-quality data, while questionable data might receive passes (green ticks).
Therefore, each module should be carefully reviewed before drawing conclusions about data quality.

:::{figure-md} raw-proc-fig-fastqc-summary
<img src="../_static/images/raw_data_processing/fastqc_example/summary.jpg" alt="Summary" class="bg-primary mb-1" width="300px">

The summary panel of a bad example.
:::

**1. Basic statistics**

The basic statistics module provides an overview of key information and statistics for the input FASTQ file, including the filename, total number of sequences, number of poor-quality sequences, sequence length, and the overall GC content (%GC) across all bases in all sequences.
High-quality single-cell data typically have very few poor-quality sequences and exhibit a uniform sequence length.
Additionally, the GC content should align with the expected GC content of the genome or transcriptome of the sequenced species.

:::{figure-md} raw-proc-fig-fastqc-basic-statistics
<img src="../_static/images/raw_data_processing/fastqc_example/basic_statistics.jpg" alt="Basic Statistics" class="bg-primary mb-1" width="800px">

A good basic statistics report example.
:::

**2. Per base sequence quality**

The per-base sequence quality view displays a box-and-whisker plot for each position in the read.
The x-axis represents the positions within the read, while the y-axis shows the quality scores.

For high-quality single-cell data, the yellow boxes—representing the interquartile range of quality scores—should fall within the green area (indicating good quality calls).
Similarly, the whiskers, which represent the 10th and 90th percentiles of the distribution, should also remain within the green area.
It is common to observe a gradual drop in quality scores along the length of the read, with some base calls at the last positions falling into the orange area (reasonable quality) due to a decreasing {term}`signal-to-noise ratio`, a characteristic of sequencing-by-synthesis methods.
However, the boxes should not extend into the red area (poor quality calls).

If poor-quality calls are observed, quality trimming may be necessary. [A more detailed explanation](https://hbctraining.github.io/Intro-to-rnaseq-hpc-salmon/lessons/qc_fastqc_assessment.html) of sequencing error profiles can be found in the [HBC training program](https://hbctraining.github.io/main/).

:::{figure-md} raw-proc-fig-fastqc-per-read-sequence-quality
<img src="../_static/images/raw_data_processing/fastqc_example/per_read_sequence_quality.jpg" alt="per read sequence quality" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per-read sequence quality graph.
:::

**3. Per tile sequence quality**

Using an Illumina library, the per-tile sequence quality plot highlights deviations from the average quality for reads across each {term}` <Flowcell>` [tile](https://www.biostars.org/p/9461090/)(miniature imaging areas of the {term}`flowcell <Flowcell>`).
The plot uses a color gradient to represent deviations, where warmer colors indicate larger deviations.
High-quality data typically display a uniform blue color across the plot, indicating consistent quality across all tiles of the flowcell.

If warm colors appear in certain areas, it suggests that only part of the flowcell experienced poor quality.
This could result from transient issues during sequencing, such as bubbles passing through the flowcell or smudges and debris within the flowcell lane.
For further investigation, consult resources like [QC Fail](https://sequencing.qcfail.com/articles/position-specific-failures-of-flowcells/) and the [common reasons for warnings](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/12%20Per%20Tile%20Sequence%20Quality.html) provided in the `FastQC` manual.

:::{figure-md} raw-proc-fig-fastqc-per-tile-sequence-quality
<img src="../_static/images/raw_data_processing/fastqc_example/per_tile_sequence_quality.jpg" alt="per tile sequence quality" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per tile sequence quality view.
:::

**4. Per sequence quality scores**

The per-sequence quality score plot displays the distribution of average quality scores for each read in the file.
The x-axis represents the average quality scores, while the y-axis shows the frequency of each score.
For high-quality data, the plot should have a single peak near the high-quality end of the scale.
If additional peaks appear, it may indicate a subset of reads with quality issues.

:::{figure-md} raw-proc-fig-fastqc-per-sequence-quality-scores
<img src="../_static/images/raw_data_processing/fastqc_example/per_sequence_quality_scores.jpg" alt="per sequence quality scores" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per sequence quality score plot.
:::

**5. Per base sequence content**

The per-base sequence content plot shows the percentage of each nucleotide (A, T, G, and C) called at each base position across all reads in the file.
For single-cell data, it is common to observe fluctuations at the start of the reads.
This occurs because the initial bases represent the sequence of the priming sites, which are often not perfectly random.
This is a frequent occurrence in RNA-seq libraries, even though `FastQC` may flag it with a warning or failure, as noted on the [QC Fail website](https://sequencing.qcfail.com/articles/positional-sequence-bias-in-random-primed-libraries/).

:::{figure-md} raw-proc-fig-fastqc-per-base-sequence-content
<img src="../_static/images/raw_data_processing/fastqc_example/per_base_sequence_content.jpg" alt="per base sequence content" class="bg-primary mb-1" width="800px">

A good (left) and bad (right) per base sequence content plot.
:::

**6. Per sequence GC content**

The per-sequence GC content plot displays the GC content distribution across all reads (in red) compared to a theoretical distribution (in blue).
The central peak of the observed distribution should align with the overall GC content of the transcriptome.
However, the observed distribution may appear wider or narrower than the theoretical one due to differences between the transcriptome's GC content and the genome's expected GC distribution.
Such variations are common and may trigger a warning or failure in `FastQC`, even if the data is acceptable.

A complex or irregular distribution in this plot, however, often indicates contamination in the library.
It is also important to note that interpreting GC content in transcriptomics can be challenging.
The expected GC distribution depends not only on the sequence composition of the transcriptome but also on gene expression levels in the sample, which are typically unknown beforehand.
As a result, some deviation from the theoretical distribution is not unusual in RNA-seq data.

:::{figure-md} raw-proc-fig-fastqc-per-sequence-gc-content
<img src="../_static/images/raw_data_processing/fastqc_example/per_sequence_gc_content.jpg" alt="Per Sequence GC Content" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per sequence GC content plot.
The plot on the left is from [the RTSF at MSU](https://rtsf.natsci.msu.edu/genomics/technical-documents/fastqc-tutorial-and-faq.aspx).
The plot on the right is taken from [the HBC training program](https://hbctraining.github.io/Intro-to-rnaseq-hpc-salmon/lessons/qc_fastqc_assessment.html).
:::

**7. Per base N content**

The per-base N content plot displays the percentage of bases at each position that were called as ``N``, indicating that the sequencer lacked sufficient confidence to assign a specific nucleotide.
In a high-quality library, the ``N`` content should remain consistently at or near zero across the entire length of the reads.
Any noticeable non-zero ``N`` content may indicate issues with sequencing quality or library preparation.


:::{figure-md} raw-proc-fig-fastqc-per-base-n-content
<img src="../_static/images/raw_data_processing/fastqc_example/per_base_n_content.jpg" alt="Per Base N Content" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per base N content plot.
:::

**8. Sequence length distribution**

The sequence length distribution graph displays the distribution of read lengths across all sequences in the file.
For most single-cell sequencing chemistries, all reads are expected to have the same length, resulting in a single peak in the graph.
However, if quality trimming was applied before the quality assessment, some variation in read lengths may be observed.
Small differences in read lengths due to trimming are normal and should not be a cause for concern if expected.

:::{figure-md} raw-proc-fig-fastqc-sequence-length-distribution
<img src="../_static/images/raw_data_processing/fastqc_example/sequence_length_distribution.jpg" alt="Sequence Length Distribution" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) sequence length distribution plot.
:::

**9. Sequence duplication levels**

The sequence duplication level plot illustrates the distribution of duplication levels for read sequences, represented by the blue line, both before and after deduplication.
In single-cell platforms, multiple rounds of {term}`PCR` are typically required, and highly expressed genes naturally produce a large number of transcripts.
Additionally, since `FastQC` is not UMI-aware (i.e., it does not account for unique molecular identifiers), it is common for a small subset of sequences to show high duplication levels.

While this may trigger a warning or failure in this module, it does not necessarily indicate a quality issue with the data.
However, the majority of sequences should still exhibit low duplication levels, reflecting a diverse and well-prepared library.

:::{figure-md} raw-proc-fig-fastqc-sequence-duplication-levels
<img src="../_static/images/raw_data_processing/fastqc_example/sequence_duplication_levels.jpg" alt="Sequence Duplication Levels" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per sequence duplication levels plot.
:::

**10. Overrepresented sequences**

The overrepresented sequences module identifies read sequences that constitute more than 0.1% of the total reads.
In single-cell sequencing, some overrepresented sequences may arise from highly expressed genes amplified during PCR.
However, the majority of sequences should not be overrepresented.

If the source of an overrepresented sequence is identified (i.e., not listed as "No Hit"), it could indicate potential contamination in the library from the corresponding source.
Such cases warrant further investigation to ensure data quality.

:::{figure-md} raw-proc-fig-fastqc-overrepresented-sequences
<img src="../_static/images/raw_data_processing/fastqc_example/overrepresented_sequences.jpg" alt="Overrepresented Sequences" class="bg-primary mb-1" width="800px">

An overrepresented sequence table.
:::

**11. Adapter content**

The adapter content module displays the cumulative percentage of reads containing {term}`adapter sequences <Adapter sequences>` at each base position.
High levels of adapter sequences indicate incomplete removal of adapters during library preparation, which can interfere with downstream analyses.
Ideally, no significant adapter content should be present in the data.
If adapter sequences are abundant, additional trimming may be necessary to improve data quality.

:::{figure-md} raw-proc-fig-fastqc-adapter-content
<img src="../_static/images/raw_data_processing/fastqc_example/adapter_content.jpg" alt="Adapter Content" class="bg-primary mb-1" width="800px">

A good (left) and a bad (right) per sequence quality score plot. The plot on the right is from [the QC Fail website](https://sequencing.qcfail.com/articles/read-through-adapters-can-appear-at-the-ends-of-sequencing-reads/).
:::

```

可以使用工具 [`MultiQC`](https://multiqc.info) 将 Multiple FastQC 报告合并为一个报告。

(raw-proc:aln-map)=

## 对齐和映射

映射或比对是单细胞原始数据处理的关键步骤。
它涉及确定每个测序片段的潜在 {term}`loci <Locus>`起源，例如与读取序列紧密匹配的基因组或转录组位置。
此步骤对于正确将读取分配到其源区域至关重要。

在单细胞测序方案中，原始序列文件通常包括：

- 小区 {term}`Barcodes <Barcode>`(CB)：各个小区的唯一标识符。
- Unique Molecular Identifiers (UMI)：区分各个分子以解决扩增偏差的标签。
- 原始 {term}`cDNA <Complementary DNA (cDNA)>`序列：从分子生成的实际读取序列。

作为第一步 ({numref}`raw-proc-fig-overview`)，准确的映射或对齐对于可靠的下游分析至关重要。
此步骤中的错误，例如读取到转录本或基因的错误映射，可能会导致计数矩阵不准确或误导。

虽然将读取序列映射到参考序列_far_早于scRNA-seq的开发，但现代scRNA-seq数据集的庞大规模（通常涉及数亿到数十亿的读取）使得这一步骤的计算量特别大。
许多现有的 RNA-seq 对准器与协议无关，并且本质上不考虑 scRNA-seq 特有的功能，例如细胞条形码、UMI 或其位置和长度。
因此，解复用和 UMI 解析 {cite}`Smith2017`等步骤通常需要额外的工具。

为了解决对齐和映射 scRNA-seq 数据的挑战，开发了几种专用工具来自动或内部处理额外的处理要求。
这些工具包括：

-`Cell Ranger`（来自 10x Genomics 的商业软件） {cite}`raw:Zheng2017`
-`zUMIs`{cite}`zumis`
-`alevin`{cite}`Srivastava2019`
-`RainDrop`{cite}`niebler2020raindrop`
-`kallisto|bustools`{cite}`Melsted2021`
-`STARsolo`{cite}`Kaminow2021`
-`alevin-fry`{cite}`raw:He2022`

这些工具提供了用于对齐 scRNA-seq 读取、解析技术读取内容（例如，细胞条形码和 UMI）、解复用和 UMI 分辨率的专门功能。
尽管它们提供简化的用户界面，但它们的内部方法有很大不同。
一些工具生成传统的中间文件，例如 {term}`BAM`文件，这些文件会被进一步处理，而其他工具则完全在内存中操作或使用紧凑的中间表示来最大限度地减少输入/输出操作并减少计算开销。

虽然这些工具的具体算法、数据结构以及时间和空间复杂性的权衡各不相同，但它们的方法通常可以沿两个轴进行分类：

1. **他们执行的映射类型**，以及
2. **它们所映射的参考序列的类型读取**。

(raw-proc:types-of-mapping)=

### 映射类型

我们重点关注常用于映射 sc/snRNA-seq 数据的三种主要映射算法：拼接对齐、连续对齐和轻量级映射的变体。

首先，我们区分基于对齐的方法和基于轻量级映射的方法 ({numref}`raw-proc-fig-alignment-mapping`)。
基于比对的方法使用各种启发式方法来识别读段可能源自的潜在基因座，然后通常使用动态编程算法对读段和参考之间的最佳核苷酸水平比对进行评分。

[global alignment](https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm) 对齐整个查询和参考序列，而 [local alignment](https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm) 专注于对齐子序列。
短读对齐通常采用半全局方法，也称为“拟合”对齐，其中大部分查询与引用的子字符串对齐。
此外，“软剪辑”可用于减少通过 ["extension" alignment](https://github.com/smarco/WFA2-lib#-33-alignment-span) 实现的读取开始或结束处的不匹配、插入或删除的惩罚。
虽然这些变体修改了动态编程递归和回溯的规则，但它们并没有从根本上改变其整体复杂性。

已经开发了几种复杂的修改和启发法来提高比对基因组测序读数的实际效率。
例如，`banded alignment`{cite}`chao1992aligning`是一种流行的启发式方法，许多工具都使用它来避免在低于阈值的比对分数不感兴趣时​​计算动态规划表的大部分内容。
其他启发式方法，例如 X-drop {cite}`zhang2000`和 Z-drop {cite}`li2018minimap2`，可以在流程早期有效地修剪无希望的对齐。
最近的进展，例如波前对准 {cite}`marco2021fast`、marco2022optimal，能够在显着减少的时间和空间内确定最佳对准，特别是在存在高分对准时。
此外，许多工作都集中在优化数据布局和计算以利用指令级并行性 {cite}`wozniak1997using, rognes2000six, farrar2007striped`，并以促进数据并行性和矢量化的方式表达动态编程递归，例如通过差异编码 {cite:t}`Suzuki2018`。
最广泛使用的对齐工具都包含这些高度优化的矢量化实现。

除了比对分数之外，产生该分数的实际比对的回溯通常被编码为`CIGAR`字符串（“Concise Idiosyncratic Gapped Alignment Report”的缩写）。
此字母数字表示形式通常存储在 SAM 或 BAM 文件输出中。
例如，`CIGAR`字符串`3M2D4M`表示比对具有三个匹配或不匹配，然后是长度为 2 的删除（表示参考中存在的碱基，但不存在读数），然后是另外四个匹配或不匹配。
扩展`CIGAR`字符串可以提供其他详细信息，例如区分匹配、不匹配或插入。
例如，`3=2D2=2X`编码与前面的示例相同的对齐方式，但指定删除之前的三个碱基是匹配的，删除之后是两个匹配的碱基和两个不匹配的碱基。
`CIGAR`字符串格式的详细说明可以在 [the SAMtools manual](https://samtools.github.io/hts-specs/SAMv1.pdf) 或 [the SAM wiki page of UMICH](https://genome.sph.umich.edu/wiki/SAM#What_is_a_CIGAR.3F) 中找到。

基于比对的方法虽然计算成本昂贵，但为读取的每个潜在映射提供质量分数。
该分数使他们能够区分读数和参考之间的高质量比对和低复杂性或“虚假”匹配。
这些方法包括传统的“完全对齐”方法，例如在`STAR`{cite}`dobin2013star`和`STARsolo`{cite}`Kaminow2021`等工具中实现的方法，以及_选择性对齐_方法，例如`salmon`{cite}`Srivastava2020Alignment`和`alevin`{cite}`Srivastava2019`中的方法，这些方法对映射进行评分，但跳过最佳对齐回溯的计算。

:::{figure-md} raw-proc-fig-alignment-mapping
<img src="../_static/images/raw_data_processing/alignment_vs_mapping.png" alt="Alignment vs Mapping" class="bg-primary mb-1" width="800px">

基于对齐的方法和基于轻量级映射的方法的抽象概述。
:::

基于比对的方法可以分为拼接比对和连续比对方法。

```{dropdown} Spliced-alignment methods
Spliced-alignment methods allow a sequence read to align across multiple distinct segments of a reference, allowing potentially large gaps between aligned regions.
These approaches are particularly useful for aligning RNA-seq reads to the genome, where reads may span {term}`splice junctions <Splice Junctions>`.
In such cases, a contiguous sequence in the read may be separated by intron and exon subsequence in the reference, potentially spanning kilobases of sequence.
Spliced alignment is especially challenging when only a small portion of a read overlaps a splice junction, as limited sequence information is available to accurately place the overhanging segment.
```

```{dropdown} Contiguous-alignment methods
Contiguous-alignment methods require a continuous substring of the reference to align well with the read.
While small insertions and deletions may be tolerated, large gaps—such as those in spliced alignments—are generally not allowed.
```

基于对齐的方法（例如拼接和连续对齐）可以与**轻量级映射方法**区分开来，后者包括诸如**伪对齐** {cite}`Bray2016`、**准映射** {cite}`srivastava2016rapmap`和**具有结构约束的伪对齐** {cite}`raw:He2022`等方法。

轻量级映射方法可实现显着更高的速度。
然而，它们不提供易于解释的基于分数的评估来确定匹配的质量，从而使得评估对齐置信度变得更加困难。

(raw-proc:mapping-references)=

### 针对不同参考序列的映射

除了选择映射算法之外，还可以选择读取映射所针对的参考序列。
参考序列主要分为三类：

- 完整的参考基因组（通常带有注释）
- 带注释的转录组
- 增强转录组

目前，并非所有映射算法和参考序列的组合都是可能的。
例如，轻量级映射算法尚不支持针对参考基因组的读数拼接映射。

(raw-proc:genome-mapping)=

#### 映射到完整基因组

用于绘图的第一种参考类型是目标生物体的**整个基因组**，通常在绘图过程中考虑带注释的转录本。
`zUMIs`{cite}`zumis`、`Cell Ranger`{cite}`raw:Zheng2017`和`STARsolo`{cite}`Kaminow2021`等工具遵循此方法。
由于许多读数源自**剪接转录本**，因此该方法需要一种**剪接感知比对算法**，能够在一个或多个剪接点之间分割比对。

这种方法的一个关键优点是它可以解释来自基因组中任何位置的读数，而不仅仅是来自注释转录本的读数。
此外，由于构建了**全基因组索引**，因此不仅报告映射到已知剪接转录本的读数，而且还报告那些重叠内含子或在非编码区域内对齐的读数，从而使该方法对于**单细胞**和**单核**数据同样有效。
另一个好处是，即使是注释转录本、外显子或内含子之外的读取映射仍然可以被考虑，从而实现量化基因座的**_事后_增强**。

(raw-proc:txome-mapping)=

#### 映射到剪接转录组

为了减少基因组剪接比对的计算开销，一种广泛采用的替代方法是仅使用带注释的转录本序列作为参考。
由于大多数单细胞实验是在小鼠或人类等模型生物体上进行的，这些生物体具有注释良好的转录组，因此基于转录组的定量可以实现与基于基因组的方法类似的读取覆盖率。

与基因组相比，转录组序列要小得多，从而显着减少了作图所需的计算资源。
此外，由于剪接模式已经在转录序列中呈现，因此这种方法消除了复杂剪接比对的需要。
相反，人们可以简单地搜索读取的连续比对或映射。
或者，可以使用连续比对来映射读数，从而使基于比对和轻量级映射技术都适合转录组参考。

虽然这些方法显着减少了比对和映射所需的内存和时间，但它们无法捕获来自剪接转录组外部的读数。
因此，它们不适合处理单核数据。
即使在单细胞实验中，来自剪接转录组外部的读数也可能构成所有数据的很大一部分，并且越来越多的证据表明此类读数应纳入后续分析{cite}`technote_10x_intronic_reads,Pool2022`。
此外，当与轻量级映射方法配合使用时，剪接转录组和生成读取的实际基因组区域之间共享的短序列可能会导致虚假映射。
反过来，这可能会导致误导甚至生物学上不可信的基因表达估计{cite}`Kaminow2021,Bruning2022Comparative,raw:He2022`。

(raw-proc:aug-txome-mapping)=

#### 映射到增强的转录组

为了解释源自剪接转录本外部的读数，可以用额外的参考序列来增强剪接转录本序列，例如全长未剪接转录本或切除的内含子序列。
与全基因组比对相比，这可以实现更好、更快、更节省内存的映射，同时仍然捕获许多否则会丢失的读数。
与仅使用剪接转录组相比，可以自信地分配更多读数，并且与轻量级映射方法结合使用时，可以显着减少虚假映射{cite}`raw:He2022`。
增强转录组广泛用于不映射到完整基因组的方法，特别是对于单核数据处理和 {term}`RNA velocity`分析 {cite}`Soneson2021Preprocessing`（参见 {doc}`../trajectories/rna_velocity`）。
这些增强参考可以为所有不依赖于全基因组 {cite}`Srivastava2019,Melsted2021,raw:He2022`剪接比对的常用方法构建。

(raw-proc:cb-correction)=

## 细胞条形码校正

基于液滴的单细胞分离系统，例如 10x Genomics 提供的系统，已成为研究细胞异质性原因和后果的重要工具。
在此分离系统中，每个捕获细胞的 RNA 材料与**条形码珠**一起在水基液滴封装内被提取。
这些珠子用独特的寡核苷酸（称为细胞条形码 (CB)）标记单个细胞的 RNA 内容，随后与从 RNA 内容逆转录的 cDNA 片段一起进行测序。
这些珠子包含高多样性的 DNA 条形码，允许对细胞的分子内容进行并行条形码编码，并将测序读数以计算机方式解复用到各个细胞箱中。

```{admonition} A note on alignment orientation

Depending on the sample chemistry and user-defined processing options, not all sequenced fragments that align to the reference are necessarily considered for quantification and barcode correction.
One commonly-applied criterion for filtering is alignment orientation.
Specifically, certain chemistries specify protocols such that the aligned reads should only derive from (i.e. map back to) the underlying transcripts in a specific orientation.
For example, in 10x Genomics 3' Chromium chemistries, we expect the biological read to align to the underlying transcript's forward strand, though anti-sense reads do exist {cite}`technote_10x_intronic_reads`.
As a result, reads mapped in the reverse-complement orientation to the reference sequences may be ignored or filtered out based on user-defined settings.
If a chemistry follows such a so-called "stranded" protocol, this should be documented.
```

### 条形码错误类型

用于单细胞分析的标签、序列和解复用方法通常是有效的。
然而，在基于液滴的文库中，观察到的细胞条形码 (CB) 的数量可能与原始封装细胞的数量存在显着差异（通常达数倍）。
这种差异是由几个关键的错误来源引起的：

- 双联体/多重联体：单个条形码可能与多个细胞相关联，导致细胞计数不足。
- 空液滴：一些液滴不含封装的细胞，并且环境 RNA 可能会被条形码标记并测序，从而导致细胞计数过多。
- 序列错误：PCR 扩增或测序过程中引入的错误可能会扭曲条形码计数，从而导致计数不足和计数过多。

为了解决这些问题，用于将 RNA-seq 读取解复用到特定细胞箱中的计算工具使用各种诊断指标来过滤掉人工数据或低质量数据。
有多种方法可用于去除环境 RNA 污染 {cite}`raw:Young2020,Muskovic2021,Lun2019`、检测双联体 {cite}`DePasquale2019,McGinnis2019,Wolock2019,Bais2019`以及根据核苷酸序列相似性纠正细胞条形码错误。

细胞条形码识别和校正采用多种常见策略。

1. **针对已知的_潜在_条形码列表进行修正**：
   某些化学物质，例如 10x 铬，从已知的潜在条形码序列库中提取 CB。
   因此，在任何样本中观察到的条形码集预计是该已知列表的子集，通常称为“白名单”。
   在这种情况下，标准方法假设：

- 任何与已知列表中的条目匹配的条形码都是正确的。
- 通过从许可列表中查找最接近的匹配（通常使用 {term}`Hamming distance`或 {term}`edit distance`）来纠正列表中没有的任何条形码。
  这种策略可以实现高效的条形码校正，但也有局限性。
  如果损坏的条形码与许可列表中的多个条形码非常相似，则其更正变得不明确。
  例如，对于取自 [10x Chromium v3 permit list](https://teichlab.github.io/scg_lib_structs/data/10X-Genomics/3M-february-2018.txt.gz) 并在单个位置突变为列表中不存在的条形码的条形码，其与许可列表中的两个或多个条形码的汉明距离 $1$ 的概率为 $\sim 81\%$。
  通过考虑仅针对已知许可列表中的条形码进行校正，可以降低此类冲突的概率，这些条形码本身恰好出现在给定样本中（或者甚至仅准确出现在给定样本中高于某个标称频率阈值的条形码）。
  此外，诸如“校正”位置处的碱基质量之类的信息可用于在校正不明确的情况下潜在地打破平局。
  然而，随着分析的细胞数量的增加，潜在细胞条形码组中序列多样性不足会增加不明确校正的频率，并且用具有不明确校正的条形码标记的读数最常被丢弃。

2. **基于膝盖或肘部的方法**：
   如果一组潜在的条形码未知，或者即使已知，但希望直接根据观察到的数据本身进行纠正，而不需要查阅外部列表，则可以使用一种基于观察的方法，即高质量条形码是与样本中最高读取次数相关的条形码。
   为了实现这一目标，我们可以构建一个累积频率图，其中条形码根据与其关联的不同读取或 UMI 的数量按降序排序。
   通常，这种排名累积频率图将包含“膝盖”或“肘部”——一个拐点，可用于表征频繁出现的条形码和不常见（因此可能是错误）条形码的特征。
   存在许多方法来尝试识别这样的拐点 {cite}`Smith2017,Lun2019,raw:He2022`作为正确捕获的细胞和空液滴之间的可能区分点。
   随后，出现在膝盖“上方”的一组条形码可以被视为许可列表，可以根据该许可列表来校正其余条形码，如上面的第一个方法列表中那样。
   这种方法很灵活，因为它可以应用于具有外部许可列表和没有外部许可列表的化学物质。
   可以改变拐点查找算法的更多参数以产生或多或少限制性的选定条形码集。
   然而，这种方法可能存在某些缺点，例如过于保守的倾向，有时在不存在明显拐点的样本中无法稳健地工作。

3. **根据预期细胞计数进行过滤和校正**：
   当条形码频率分布由于技术问题而缺乏清晰的拐点或显示双峰模式时，可以通过用户提供的预期细胞计数来指导条形码校正。
   在这种方法中，用户提供对所分析细胞的预期数量的估计。
   然后，条形码按频率降序排序，获得接近预期细胞计数的稳健分位数索引处的频率 $f$，并且频率在 $f$ 的小常数分数（例如 $\ge \frac{f}{10}$）内的所有细胞都被视为有效条形码。
   再次，通过尝试基于序列相似性对这些有效条形码之一进行唯一校正，针对该有效列表来校正剩余条形码。

4. **基于有效单元格的强制数量进行过滤**：
   最简单的方法（尽管可能存在问题）是用户手动指定有效条形码的数量。

- 用户在排序的条形码频率列表中选择索引。
- 所有高于此阈值的条形码均被视为有效。
- 使用标准的基于相似性的校正方法根据此列表校正剩余的条形码。
  虽然这保证了至少 n 个单元的选择，但它假设所选择的阈值准确地反映了真实单元的数量。
  仅当用户有充分的理由相信阈值频率应围绕所提供的索引设置时，这才是合理的。

(raw-proc:umi-resolution)=

## UMI 分辨率

细胞条形码 (CB) 校正后，读数要么被丢弃，要么分配给校正后的 CB。
随后，我们希望量化每个校正的 CB 中每个基因的丰度。

由于 {ref}`exp-data:transcript-quantification`中讨论的 {term}`amplification bias`，必须根据 UMI 来对读取进行重复数据删除，以评估采样分子的真实计数 ({numref}`umi-figure`)。此外，在尝试执行此估计时，其他几个复杂因素也带来了挑战。

UMI 重复数据删除步骤旨在识别来自实验中捕获和测序的每个细胞中的每个原始、前PCR 分子的读数和UMI 集。
该过程的结果是将分子计数分配给每个细胞中的每个基因，随后在下游分析中用作该基因的原始表达估计。
我们将查看观察到的 UMI 的集合及其相关的映射读数并尝试推断每个基因产生的观察到的分子的原始数量的过程称为“UMI 解析”过程。

为了简化解释，映射到参考（例如，基因的基因组位点）的读数被称为该参考的读数，并且它们的 UMI 标签被称为该参考的 UMI。
与特定 UMI 关联的读取集称为该 UMI 的读取。

一次读取只能由一个 UMI 标记，但如果它映射到多个引用，则可能属于多个引用。
此外，由于 scRNA-seq 中的分子条形码对于每个细胞来说通常是隔离和独​​立的（除了前面讨论的解析细胞条形码的挑战之外），因此将针对单个细胞解释 _UMI 分辨率_，而不失一般性。
该相同的过程通常独立地应用于所有单元。

```{figure} ../_static/images/raw_data_processing/UMI.png
:name: umi-figure
:alt: Figure UMIs
:with: 100%


UMIs reduce PCR amplification bias by tracking original molecules, but can be affected by different types of errors (blue boxes).
Nucleotide substitutions in UMI tags may occur during amplification or sequencing.
Multimapping can arise when reads sharing the same UMI are mapped to different genes (blue and red), when a single read maps to multiple genes (gray), or both.
```

(raw-proc:need-for-umi-resolution)=

### 需要 UMI 分辨率

在理想情况下，在正确的（未改变的）UMI 标签读取的情况下，每个 UMI 的读取唯一地映射到公共参考基因，并且 UMI 和前 PCR 分子之间存在双射。
因此，UMI 重复数据删除过程在概念上很简单：UMI 的读取是来自单个前 PCR 分子的 PCR 重复项。
每个基因捕获和测序的分子数量是针对该基因观察到的不同 UMI 的数量。

然而，实践中遇到的问题使得上述简单规则不足以识别一般UMIs的基因起源，因此需要开发更复杂的模型（{numref}`umi-figure`）：

- **UMI 中的错误**：
  当读取的测序 UMI 标签包含 PCR 或测序过程中引入的错误时，就会发生这些情况。
  常见的 UMI 错误包括 PCR 期间的核苷酸替换和测序期间的读取错误。
  如果未能解决此类 UMI 错误，可能会夸大分子的估计数量 {cite}`Smith2017,ziegenhain2022molecular`。

- **多重映射**：
  当读取或 UMI 属于多个引用（例如，多基因读取/UMI）时，会出现此问题。
  当 UMI 的不同读取映射到不同基因时、当读取映射到多个基因或两者兼而有之时，就会发生这种情况。
  这个问题的后果是多基因读取/UMIs 的基因起源不明确，这导致这些基因的采样前 PCR 分子计数不确定。
  简单地丢弃多基因读数/UMI 可能会导致数据丢失或倾向于产生多重映射读数的基因之间的偏差估计，例如序列相似的基因家族 {cite}`Srivastava2019`。

```{admonition} A Note on UMI Errors
UMI errors, especially those due to nucleotide substitutions and miscallings, are prevalent in single-cell experiments.
{cite:t}`Smith2017` establish that the average number of bases different (edit distance) between the observed UMI sequences in the tested single-cell experiments is lower than randomly sampled UMI sequences, and the enrichment of low edit distances is well correlated with the degree of PCR amplification.
Multimapping also exists in single-cell data and, depending upon the gene being considered, can occur at a non-trivial rate.
{cite:t}`Srivastava2019` show that discarding the multimapping reads can negatively bias the predicted molecule counts.
```

还存在我们在此不关注的其他挑战，例如“趋同”和“发散”UMI 碰撞。
我们考虑使用相同的 UMI 来标记同一细胞中同一基因产生的两个不同的前 PCR 分子的情况，作为聚合碰撞。
当两个或多个不同的 UMI 由相同的 pre-PCR 分子产生时，例如，由于从该分子中采样了多个引发位点，我们认为这是发散碰撞。
我们预计聚合 UMI 碰撞很少见，因此其影响通常很小。
此外，转录本级映射信息有时可用于解决此类冲突{cite}`Srivastava2019`。
不同的 UMI 碰撞主要发生在未剪接转录本 {cite}`technote_10x_intronic_reads`的内含子之间，解决它们提出的问题的方法是一个活跃的研究领域 {cite}`technote_10x_intronic_reads,Gorin2021`。

鉴于 UMI 的使用在高通量 scRNA-seq 协议中几乎无处不在，并且解决这些错误可以改善基因丰度的估计，因此最近的文献 {cite}`Islam2013,Bose2015,raw:Macosko2015,Smith2017,Srivastava2019,Kaminow2021,Melsted2021,raw:He2022,calib,umic,zumis`中对 UMI 分辨率的问题给予了很多关注。

```{dropdown} Graph-based UMI resolution

(raw-proc:graph-based-umi-resolution)=

### Graph-based UMI resolution

As a result of the problems that arise when attempting to resolve UMIs, many methods have been developed to address the problem of UMI resolution.
While there are a host of different approaches for UMI resolution, we will focus on a framework for representing problem instances, modified from a framework initially proposed by {cite:t}`Smith2017`, that relies upon the notion of a _UMI graph_.
Each connected component of this graph represents a sub-problem wherein certain subsets of UMIs are collapsed (i.e., resolved as evidence of the same pre-PCR molecule).
Many popular UMI resolution approaches can be interpreted in this framework by simply modifying precisely how the graph is refined and how the collapse or resolution procedure carried out over this graph works.

In the context of single-cell data, a UMI graph $G(V,E)$ is a {term}`directed graph` with a node set $V$ and an edge set $E$.
Each node $v_i \in V$ represents an equivalence class (EC) of reads, and the edge set $E$ encodes the relationship between the ECs.
The equivalence relation $\sim_r$ defined on reads is based on their UMI and mapping information.
We say reads $r_x$ and $r_y$ are equivalent, $r_x \sim_r r_y$, if and only if they have identical UMI tags and map to the same set of references.
UMI resolution approaches may define a "reference" as a genomic locus {cite}`Smith2017`, transcript {cite}`Srivastava2019,raw:He2022` or gene {cite}`raw:Zheng2017,Kaminow2021`.

In the UMI graph framework, a UMI resolution approach can be divided into three major steps:
**defining nodes**, **defining adjacency relationships**, and **resolving components**.
Each of these steps has different options that can be modularly composed by different approaches.
Additionally, these steps may sometimes be preceded (and/or followed) by filtering steps designed to discard or heuristically assign (by modifying the set of reference mappings reported) reads and UMIs exhibiting certain types of mapping ambiguity.

(raw-proc:umi-graph-node-def)=

#### Defining nodes

As described above, a node $v_i \in V$ is an equivalence class of reads.
Therefore, $V$ can be defined based on the full or filtered set of mapped reads and their associated _uncorrected_ UMIs.
All reads that satisfy the equivalence relation $\sim_r$ based on their reference set and UMI tag are associated with the same vertex $v \in V$.
An EC is a multi-gene EC if its UMI is a multi-gene UMI.
Some approaches will avoid the creation of such ECs by filtering or heuristically assigning reads prior to node creation, while other approaches will retain and process these ambiguous vertices and attempt and resolve their gene origin via parsimony, probabilistic assignment, or based on a related rule or model {cite}`Srivastava2019,Kaminow2021,raw:He2022`.

(raw-proc:umi-graph-edge-def)=

#### Defining the adjacency relationship

After creating the node set $V$ of a UMI graph, the adjacency of nodes in $V$ is defined based on the distance, typically the Hamming or edit distance, between their UMI sequences and, optionally, the content of their associated reference sets.

Here we define the following functions on the node $v_i \in V$:

- $u(v_i)$ is the UMI tag of $v_i$.
- $c(v_i) = |v_i|$ is the cardinality of $v_i$, i.e., the number of reads associated with $v_i$ that are equivalent under $\sim_r$.
- $m(v_i)$ is the reference set encoded in the mapping information, for $v_i$.
- $D(v_i, v_j)$ is the distance between $u(v_i)$ and $u(v_j)$, where $v_j \in V$.

Given these function definitions, any two nodes $v_i, v_j \in V$ will be incident with a bi-directed edge if and only if $m(v_i) \cap m(v_j) \ne \emptyset$ and $D(v_i,v_j) \le \theta$, where $\theta$ is a distance threshold and is often set as $\theta=1$ {cite}`Smith2017,Kaminow2021,Srivastava2019`.
Additionally, the bi-directed edge might be replaced by a directed edge incident from $v_i$ to $v_j$ if $c(v_i) \ge 2c(v_j) -1$ or vice versa {cite}`Smith2017,Srivastava2019`.
Though these edge definitions are among the most common, others are possible, so long as they are completely defined by the $u$, $c$, $m$, and $D$ functions. With $V$ and $E$ in hand, the UMI graph $G = (V,E)$ is now defined.

(raw-proc:umi-graph-resolution-def)=

#### Defining the graph resolution approach

Given the defined UMI graph, many different resolution approaches may be applied.
A resolution method may be as simple as finding the set of connected components, clustering the graph, greedily collapsing nodes or contracting edges {cite}`Smith2017`, or searching for a cover of the graph by structures following certain rules (e.g., monochromatic arboresences {cite}`Srivastava2019`) to reduce the graph.
As a result, each node in the reduced UMI graph, or each element in the cover in the case that the graph is not modified dynamically, represents a pre-PCR molecule.
The collapsed nodes or covering sets are regarded as the PCR duplicates of that molecule.

Different rules for defining the adjacency relationship and different approaches for graph resolution itself can seek to preserve different properties and can define a wide variety of distinct overall UMI resolution approaches.
For approaches that probabilistically resolve ambiguity caused by multimapping, the resolved UMI graph may contain multi-gene equivalence classes (ECs), with their gene origins determined in the next step.

Other UMI resolution approaches exist, for example, the reference-free model {cite}`umic` and the method of moments {cite}`Melsted2021`, but they may not be easily represented in this framework and are not discussed in further detail here.

```

(raw-proc:umi-graph-quantification)=

#### 量化

UMI 解析的最后一步是使用解析的 UMI 图量化每个基因的丰度。
对于丢弃多基因 EC 的方法，通过计算每个基因标记的 EC 的数量来生成当前正在处理的细胞中基因的分子计数向量（或简称计数向量）。
另一方面，处理而不是丢弃多基因 EC 的方法通常通过应用一些统计推断程序来解决歧义。
例如，{cite:t}`Srivastava2019`引入了用于概率分配多基因UMI的期望最大化（EM）方法，并且相关的EM算法也作为可选步骤引入了后续工具{cite}`Melsted2021,Kaminow2021,raw:He2022`中。
在该模型中，折叠的 EC 到基因的分配是潜在变量，基因的去重复分子计数是主要参数。
直观上，来自基因独特 EC 的证据将用于帮助概率分配多基因 EC。
The EM 算法寻找共同具有生成观察到的 EC 的（局部）最高可能性的参数。

通常，上述 UMI 分辨率和定量过程将针对每个细胞单独执行，由校正的 CB 表示，以创建所有细胞中所有基因的完整计数矩阵。
然而，高通量单细胞样本中每个细胞信息的相对缺乏限制了执行 UMI 分辨率时可用的证据，这反过来又限制了基于模型的解决方案（如上述统计推断程序）的潜在功效。

(raw-proc:count-qc)=

## 计数矩阵质量控制

生成计数矩阵后，执行质量控制 (QC) 评估非常重要。
有几种不同的评估通常属于质量控制的范畴。
通常会记录和报告基本的全局指标，以帮助评估测序测量本身的整体质量。
这些指标包括映射读数的总分数、每个细胞观察到的不同 UMI 的分布、UMI 重复数据删除率的分布、每个细胞检测到的基因的分布等数量。
这些和类似的指标通常由量化工具本身 {cite}`raw:Zheng2017,Kaminow2021,Melsted2021,raw:He2022`记录，因为它们自然产生，并且可以在读取映射、细胞条形码校正和 UMI 解析过程中计算。
同样，有多种工具可以帮助组织和可视化这些基本指标，例如 [Loupe browser](https://support.10xgenomics.com/single-cell-gene-expression/software/visualization/latest/what-is-loupe-cell-browser)、[alevinQC](https://github.com/csoneson/alevinQC) 或 [kb_python report](https://github.com/pachterlab/kb_python)，具体取决于所使用的量化管道。
除了这些基本的全局指标之外，在这个分析阶段，QC 指标主要旨在帮助确定哪些细胞 (CB) 已“成功”测序，以及哪些细胞表现出需要过滤或纠正的伪影。

在下面的切换部分中，我们讨论取自`alevinQC`[manual webpage](https://github.com/csoneson/alevinQC) 的 alevinQC 报告示例。

```{toggle}

Once `alevin` or `alevin-fry` quantifies the single-cell data, the quality of the data can be assessed through the R package [`alevinQC`](https://github.com/csoneson/alevinQC).
The alevinQC report can be generated in PDF format or as R/Shiny applications, which summarizes various components of the single-cell library, such as reads, CBs, and UMIs.

**1. Metadata and summary tables**

:::{figure-md} raw-proc-fig-alevinqc-summary
<img src="../_static/images/raw_data_processing/alevinQC_summary.png" alt="AlevinQC Summary" class="bg-primary mb-1" width="800px">

An example of the summary section of an alevinQC report.
:::

The first section of an alevinQC report shows a summary of the input files and the processing result, among which, the top left table displays the metadata provided by `alevin` (or `alevin-fry`) for the quantification results.
For example, this includes the time of the run, the version of the tool, and the path to the input FASTQ and index files.
The top right summary table provides the summary statistics for various components of the single-cell library, for example, the number of sequencing reads, the number of selected cell barcodes at various levels of filtering, and the total number of deduplicated UMIs.

**2. Knee plot, initial whitelist determination**

:::{figure-md} raw-proc-fig-alevinqc-plots
<img src="../_static/images/raw_data_processing/alevinQC_plots.png" alt="AlevinQC Plots" class="bg-primary mb-1" width="800px">

The figure shows the plots in the alevinQC report of an example single-cell dataset, of which the cells are filtered using the "knee" finding method.
Each dot represents a corrected cell barcode with its corrected profile.
:::

The first (top left) view in {numref}`raw-proc-fig-alevinqc-plots` shows the distribution of cell barcode frequency in decreasing order.
In all plots shown above, each point represents a corrected cell barcode, with its x-coordinate corresponding to its cell barcode frequency rank.
In the top left plot, the y-coordinate corresponds to the observed frequency of the corrected barcode.
Generally, this plot shows a "knee"-like pattern, which can be used to identify the initial list of high-quality barcodes.
The red dots in the plot represent the cell barcodes selected as the high-quality cell barcodes in the case that "knee"-based filtering was applied.
In other words, these cell barcodes contain a sufficient number of reads to be deemed high-quality and likely derived from truly present cells.
Suppose an external permit list is passed in the CB correction step, which implies no internal algorithm was used to distinguish high-quality cell barcodes.
In that case, all dots in the plot will be colored red, as all these corrected cell barcodes are processed throughout the raw data processing pipeline and reported in the gene count matrix.
One should be skeptical of the data quality if the frequency is consistently low across all cell barcodes.

**3. Barcode collapsing**

After identification of the barcodes that will be processed, either through an internal threshold (e.g., from the "knee"-based method) or through external whitelisting, `alevin` (or `alevin-fry`) performs cell barcode sequence correction.
The barcode collapsing plot, the upper middle plot in the {numref}`raw-proc-fig-alevinqc-plots`, shows the number of reads assigned to a cell barcode after sequence correction of the cell barcodes versus prior to correction.
Generally, we would see that all points fall close to the line representing $x = y$, which means that the reassignments in CB correction usually do not drastically change the profile of the cell barcodes.

**4. Knee Plot, number of genes per cell**

The upper right plot in {numref}`raw-proc-fig-alevinqc-plots` shows the distribution of the number of observed genes of all processed cell barcodes.
Generally, a mean of $2,000$ genes per cell is considered modest but reasonable for the downstream analyses.
One should double-check the quality of the data if all cells have a low number of observed genes.

**5. Quantification summary**

Finally, a series of quantification summary plots, the bottom plots in {numref}`raw-proc-fig-alevinqc-plots`, compare the cell barcode frequency, the total number of UMIs after deduplication and the total number of non-zero genes using scatter plots.
In general, in each plot, the plotted data should demonstrate a positive correlation, and, if high-quality filtering (e.g., knee filtering) has been performed, the high-quality cell barcodes should be well separated from the rest.
Moreover, one should expect all three plots to convey similar trends.
If using an external permit list, all the dots in the plots will be colored red, as all these cell barcodes are processed and reported in the gene count matrix.
Still, we should see the correlation between the plots and the separation of the dots representing high-quality cells to others.
If all of these metrics are consistently low across cells or if these plots convey substantially different trends, then one should be concerned about the data quality.

```

### 空滴检测

第一个 QC 步骤之一是确定哪些细胞条形码对应于“高置信度”测序细胞。
在基于液滴的协议 {cite}`raw:Macosko2015`中，某些条形码与环境 {term}`RNA`而不是捕获细胞的 RNA 相关联，这是常见的。
当液滴无法捕获细胞时就会发生这种情况。
这些空滴仍然倾向于产生测序读数，尽管这些读数的特征看起来与与正确捕获的细胞相对应的条形码相关的特征明显不同。
存在许多方法来评估条形码是否可能对应于空液滴。
一种简单的方法是检查条形码的累积频率图，其中条形码按照与其关联的不同 UMI 数量的降序排列。
该图通常包含一个“膝盖”，可以将其识别为正确捕获的细胞和空液滴 {cite}`Smith2017,raw:He2022`之间的可能区分点。
虽然这种“膝盖”方法很直观并且通常可以估计合理的阈值，但它有几个缺点。
例如，并非所有累积直方图都显示明显的拐点，并且众所周知，设计能够稳健且自动检测此类拐点的算法非常困难。
最后，与条形码相关的总 UMI 计数可能不是单独确定条形码是否与空或损坏的细胞相关的最佳信号。

这导致了几种专门设计用于检测空的或损坏的液滴或通常被认为是“低质量”的细胞{cite}`Lun2019,Heiser2021,Hippen2021,Muskovic2021,Alvarez2020,raw:Young2020`的工具的开发。
这些工具结合了各种不同的细胞质量测量方法，包括不同 UMI 的频率、检测到的基因数量以及线粒体 RNA 的分数，并且通常通过对这些特征应用统计模型来将高质量细胞与假定的空液滴或受损细胞进行分类。
这意味着通常可以对单元进行评分，并且可以基于单元不为空或受损的估计后验概率来选择最终过滤。
虽然这些模型通常适用于单细胞 {term}`RNA`-seq 数据，但可能需要应用几个额外的过滤器或启发式方法才能在单核 {term}`RNA`-seq 数据 {cite}`Kaminow2021,raw:He2022`中获得稳健的过滤，就像`DropletUtils`{cite}`Lun2019`的 [`emptyDropsCellRanger`](https://github.com/MarioniLab/DropletUtils/blob/master/R/emptyDropsCellRanger.R) 函数中公开的那些模型一样。

### 双峰检测

除了确定哪些细胞条形码对应于空滴或受损细胞之外，人们还可能希望识别那些对应于双联体或多联体的细胞条形码。
当给定的液滴捕获两个（双联体）或更多（多联体）细胞时，这可能会导致这些细胞条形码在数量上出现偏态分布，例如它们代表的读数和 UMI 数量，以及它们显示的基因表达谱。
还开发了许多工具来预测细胞条形码 {cite}`DePasquale2019,McGinnis2019,Wolock2019,Bais2019,Bernstein2020`的双峰状态。
一旦检测到，被确定为可能是双联体和多重联体的细胞可以被去除或以其他方式在后续分析中进行调整。

(raw-proc:output-representation)=

## 计数数据表示

当完成最初的原始数据处理和质量控制并继续进行后续分析时，重要的是要承认并记住逐个基因计数矩阵充其量只是原始样本中测序分子的近似值。
在原始数据处理管道的几个阶段，应用启发式方法，并进行简化以生成该计数矩阵。
例如，读取映射和细胞条形码校正都是不完美的。
准确解析 UMI 特别具有挑战性，并且与附加到多重映射读取的 UMI 相关的问题经常被忽视。
此外，多个引发位点，特别是在未剪接的分子中，可能会违反通常假设的一分子对一 UMI 关系。

## 简要讨论

为了结束本章，我们传达了一些观察结果和建议，这些观察结果和建议来自最近围绕上述 {cite}`You_2021,Bruning_2022`描述的一些常见预处理工具的基准测试和回顾研究。
当然，值得注意的是，单细胞和单核 RNA-seq 原始数据处理的方法和工具的开发以及对此类方法的持续评估是社区持续努力的结果。
因此，在进行自己的分析时，尝试几种不同的工具通常是有用且合理的。

在最粗略的层面上，最常见的工具可以稳健而准确地处理数据。
有人建议，对于许多常见的下游分析（例如聚类）以及用于执行这些分析的方法，预处理工具的选择通常比分析过程 {cite}`You_2021`中的其他步骤产生的差异较小。
尽管如此，也有人观察到，应用仅限于剪接转录组的轻量级映射可以增加虚假映射和基因表达 {cite}`Bruning_2022`的可能性。

最终，特定工具的选择很大程度上取决于手头的任务以及可用计算资源的限制。
如果执行标准的单细胞分析，基于轻量级映射的方法是一个不错的选择，因为它们比现有的基于比对的工具更快（通常相当快）并且更节省内存。
如果执行单核 RNA-seq 分析，`alevin-fry`是一个特别有吸引力的选择，因为它仍然节省内存，并且即使转录组参考扩展到包括未剪接的参考序列，其索引仍然相对较小。
另一方面，当恢复（扩展）转录组之外的图谱很重要的读数或下游分析需要基因组作图位点时，建议使用基于比对的方法。
这对于使用`sierra`{cite}`sierra`等工具进行差异转录本使用分析等任务尤其相关。
在基于对齐的管道中，根据{cite:t}`Bruning_2022`，`STARsolo`应该优于`Cell Ranger`，因为前者比后者快得多，并且需要更少的内存，同时它也能够产生几乎相同的结果。

(raw-proc:example-workflow)=

## 一个真实的例子

鉴于我们已经涵盖了各种原始数据处理方法背后的概念，我们现在将注意力转向演示如何使用特定工具（在本例中为`alevin-fry`）来处理小型示例数据集。
首先，我们需要 [FASTQ format](https://en.wikipedia.org/wiki/FASTQ_format) 中单细胞实验的测序读数以及读数将被映射的参考（例如转录组）。
通常，参考文献包括已测序物种的基因组序列和相应的基因注释，分别采用 [FASTA](https://en.wikipedia.org/wiki/FASTA_format) 和 [GTF](https://useast.ensembl.org/info/website/upload/gff.html) 格式。

在此示例中，我们将使用人类基因组的_染色体 5_ 及其相关基因注释作为参考，它是人类参考的子集，[GRCh38 (GENCODE v32/Ensembl 98) reference](https://support.10xgenomics.com/single-cell-gene-expression/software/release-notes/build#GRCh38_2020A) 来自 10x 基因组参考构建。
相应地，我们从 10x Genomics 的 [human brain tumor dataset](https://www.10xgenomics.com/resources/datasets/200-sorted-cells-from-human-glioblastoma-multiforme-3-lt-v-3-1-3-1-low-6-0-0) 中提取映射到生成参考的读取子集。

[`Alevin-fry`](https://alevin-fry.readthedocs.io/en/latest/) {cite}`raw:He2022`是一种快速、准确且节省内存的单细胞和单核数据处理工具。
[Simpleaf](https://github.com/COMBINE-lab/simpleaf) 是一个用 [rust](https://www.rust-lang.org/) 编写的程序，它公开了一个统一且简化的接口，用于使用`alevin-fry`管道处理一些最常见的协议和数据类型。
基于 nextflow 的 [workflow](https://github.com/COMBINE-lab/quantaf) 工具还可以处理大量的单细胞数据。
这里我们将首先展示如何使用两个`simpleaf`命令处理单细胞原始数据。然后，我们描述与这些`simpleaf`命令对应的完整的`salmon alevin`和`alevin-fry`命令集，以概述本节中描述的步骤发生的位置并传达可能的不同处理选项。
这些命令将从命令行运行，并且 [`conda`](https://docs.conda.io/en/latest/) 将用于安装运行此示例所需的所有软件。

(raw-proc:example-prep)=

### 准备

在开始之前，我们在终端中创建一个 conda 环境并安装所需的包。
`Simpleaf`取决于 [`alevin-fry`](https://alevin-fry.readthedocs.io/en/latest/)、[`salmon`](https://salmon.readthedocs.io/en/latest/) 和 [`pyroe`](https://github.com/COMBINE-lab/pyroe)。
它们均在`bioconda`上可用，并且在安装`simpleaf`时会自动安装。

```bash
conda create -n af -y -c bioconda simpleaf
conda activate af
```

````{admonition} Note on using an Apple silicon-based device

Conda does not currently build most packages natively for Apple silicon.
Therefore, if you are using a non-Intel-based Apple computer (e.g., with an M1 (Pro/Max/Ultra) or M2 chip),
you should make sure to specify that your environment uses the Rosetta2 translation layer.
To do this, you can replace the above commands with the following (instructions adopted
from [here](https://github.com/Haydnspass/miniforge#rosetta-on-mac-with-apple-silicon-hardware)):

```bash
CONDA_SUBDIR=osx-64 conda create -n af -y -c bioconda simpleaf # 创建一个新环境
conda 激活 af
conda env config vars set CONDA_SUBDIR=osx-64 # 后续命令使用 intel 软件包
````

Next, we create a working directory, `af_xmpl_run`, and download and uncompress the example dataset from a remote host.

```bash
# 创建工作目录并进入工作目录
## && 运算符帮助使用一行代码执行两个命令。
mkdir af_xmpl_run && cd af_xmpl_run

# 获取示例数据集和CB许可列表并解压
## 管道运算符 (|) 将 wget 命令的输出传递给 tar 命令。
##`tar xzf`之后的破折号运算符 (-) 捕获第一个命令的输出。
## - 示例数据集
wget -qO- https://umd.box.com/shared/static/lx2xownlrhz3us8496tyu9c4dgade814.gz | tar xzf - --strip-components=1 -C .
## 包含 fastq 文件的获取文件夹称为 toy_read_fastq。
fastq_dir="toy_read_fastq"
## 获取的包含人类参考文件的文件夹称为 toy_ human_ref。
ref_dir =“玩具_人类_参考”

# Fetch CB 许可证列表
## 右侧 V 形 (>) 将 STDOUT 重定向到文件。
wget -qO- https://github.com/f0t1h/3M-february-2018/raw/master/3M-february-2018.txt.gz | gunzip - > 3M-february-2018.txt

```

With the reference files (the genome FASTA file and the gene annotation GTF file) and read records (the FASTQ files) ready, we can now apply the raw data processing pipeline discussed above to generate the gene count matrix.

(raw-proc:example-simpleaf)=

### Simplified raw data processing pipeline

[Simpleaf](https://github.com/COMBINE-lab/simpleaf) is designed to simplify the `alevin-fry` interface for single-cell and nucleus raw data processing. It encapsulates the whole processing pipeline into two steps:

1. [`simpleaf index`](https://simpleaf.readthedocs.io/en/latest/index-command.html) indexes the provided reference or makes a _splici_ reference (<u>splic</u>ed transcripts + <u>i</u>ntrons) and index it.
2. [`simpleaf quant`](https://simpleaf.readthedocs.io/en/latest/quant-command.html) maps the sequencing reads against the indexed reference and quantifies the mapping records to generate a gene count matrix.

More advanced usages and options for mapping with `simpleaf` can be found [here](https://simpleaf.readthedocs.io/en/latest/).

When running `simpleaf index`, if a genome FASTA file (`-f`) and a gene annotation GTF file(`-g`) are provided, it will generate a _splici_ reference and index it; if only a transcriptome FASTA file is provided (`--refseq`), it will directly index it. Currently, we recommend the _splici_ index.

```bash
# simpleaf需要环境变量ALEVIN_FRY_HOME来存储配置和数据。
# 例如它使用的底层程序的路径和CB许可列表
mkdir alevin_fry_home && 导出ALEVIN_FRY_HOME='alevin_fry_home'

# simpleaf set-paths 命令查找所需工具的路径，并在ALEVIN_FRY_HOME 文件夹中写入配置JSON 文件。
simpleaf 设置路径

# simpleaf 索引
# 用法：simpleaf索引-o out_dir [-f基因组_fasta -g基因_注释_GTF|--refseq转录组_fasta] -r read_length -t number_of_threads
## -r read_lengh 是测序仪生成生物读数（Illumina 中的 read2）所执行的测序循环数。
## 公开可用的数据集通常在描述中包含读取长度。有时它们被称为循环数。
simpleaf 索引 \
- o simpleaf_index \
- f toy_ human_ref/fasta/genome.fa \
- g toy_human_ref/genes/genes.gtf \
- r 90 \
- t 8
```

In the output directory `simpleaf_index`, the `ref` folder contains the _splici_ reference; The `index` folder contains the salmon index built upon the _splici_ reference.

The next step, `simpleaf quant`, consumes an index directory and the mapping record FASTQ files to generate a gene count matrix. This command encapsulates all the major steps discussed in this section, including mapping, cell barcode correction, and UMI resolution.

```bash
# 收集测序读取文件
## reads1 和reads2 变量是通过从toy_read_fastq 目录中查找具有模式“_R1_”和“_R2_”的文件名来定义的。
读取1_pat =“_R1_”
reads2_pat =“_R2_”

## 读取的文件必须排序并用逗号分隔。
### find 命令查找 fastq_dir 中具有名称模式的文件
### sort命令对文件名进行排序
### awk 命令和粘贴命令一起将文件名转换为逗号分隔的字符串。
read1="$(find -L ${fastq_dir} -name "*$reads1_pat*" -type f | sort | awk -v OFS=, '{$1=$1;print}' |粘贴-sd，）”
read2="$(find -L ${fastq_dir} -name "*$reads2_pat*" -type f | sort | awk -v OFS=, '{$1=$1;print}' |粘贴-sd，）”

# simpleaf 定量
## 用法： simpleaf quant -cchemistry -tthreads -1reads1 -2reads2 -iindex -u [未拼接许可列表] -rresolution -mt2g_3col -ooutput_dir
simpleaf 定量 \
- c 10xv3 -t 8 \
- 1 $reads1 -2 $reads2 \
- i simpleaf_index/索引 \
- u -r 类似 cr \
- m simpleaf_index/index/t2g_3col.tsv \
- o simpleaf_quant
```

After running these commands, the resulting quantification information can be found in the `simpleaf_quant/af_quant/alevin` folder.
Within this directory, there are three files: `quants_mat.mtx`, `quants_mat_cols.txt`, and `quants_mat_rows.txt`, which correspond, respectively, to the count matrix, the gene names for each column of this matrix, and the corrected, filtered cell barcodes for each row of this matrix. The tail lines of these files are shown below.
Of note here is the fact that `alevin-fry` was run in the USA-mode (<u>u</u>nspliced, <u>s</u>pliced, and <u>a</u>mbiguous mode), and so quantification was performed for both the spliced and unspliced status of each gene — the resulting `quants_mat_cols.txt` file will then have a number of rows equal to 3 times the number of annotated genes which correspond, to the names used for the spliced (S), unspliced (U), and splicing-ambiguous variants (A) of each gene.

```bash
#`quants_mat.mtx`中的每一行代表
# 格式行列条目中的非零条目
$ 尾部 -3 simpleaf_quant/af_quant/alevin/quants_mat.mtx
138 58 1
139 9 1
139 37 1

#`quants_mat_cols.txt`中的每一行都是一个熔接状态
基因的编号，格式为（基因名称）-（剪接状态）
$ tail -3 simpleaf_quant/af_quant/alevin/quants_mat_cols.txt
ENSG00000120705-A
ENSG00000198961-A
ENSG00000245526-A

#`quants_mat_rows.txt`中的每一行都是更正后的
# （并且可能经过过滤）单元格条形码
$ tail -3 simpleaf_quant/af_quant/alevin/quants_mat_rows.txt
TTCGATTTCTGAATCG
TGCTCGTGTTCGAAGG
ACTGTGAAGAAATTGC
```

We can load the count matrix into Python as an [`AnnData`](https://anndata.readthedocs.io/en/latest/) object using the `load_fry` function from [`pyroe`](https://github.com/COMBINE-lab/pyroe).
A similar function, [loadFry](https://rdrr.io/github/mikelove/fishpond/man/loadFry.html), has been implemented in the [`fishpond`](https://github.com/mikelove/fishpond) R package.

```python
进口火爆

quant_dir = 'simpleaf_quant/af_quant'
adata_sa = Pyroe.load_fry(quant_dir)
```

The default behavior loads the `X` layer of the `Anndata` object as the sum of the spliced and ambiguous counts for each gene.
However, recent work {cite}`Pool2022` and [updated practices](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/release-notes) suggest that the inclusion of intronic counts, even in single-cell RNA-seq data, may increase sensitivity and benefit downstream analyses.
While the best way to make use of this information is the subject of ongoing research, since `alevin-fry` automatically quantifies spliced, unspliced, and ambiguous reads in each sample, the count matrix containing the total counts for each gene can be simply obtained as follows:

```python
进口火爆

quant_dir = 'simpleaf_quant/af_quant'
adata_usa =pyroe.load_fry(quant_dir,output_format={'X' : ['U','S','A']})
```

(raw-proc:example-map)=

### The complete alevin-fry pipeline

`Simpleaf` makes it possible to process single-cell raw data in the "standard" way with a few commands.
Next, we will show how to generate the identical quantification result by explicitly calling the `pyroe`, `salmon`, and `alevin-fry` commands.
On top of the pedagogical value, knowing the exact command of each step will be helpful if only a part of the pipeline needs to be rerun or if some parameters not currently exposed by `simpleaf` need to be specified.

Please note that the commands in the {ref}`raw-proc:example-prep` section should be executed in advance.
All the tools called in the following commands, `pyroe`, `salmon`, and `alevin-fry`, have already been installed when installing `simpleaf`.

#### Building the index

First, we process the genome FASTA file and gene annotation GTF file to obtain the _splici_ index.
The commands in the following code chunk are analogous to the `simpleaf index` command discussed above. This includes two steps:

1. Building the _splici_ reference (<u>splic</u>ed transcripts + <u>i</u>ntrons) by calling `pyroe make-splici`, using the genome and gene annotation file
2. Indexing the _splici_ reference by calling `salmon index`

```bash
# 进行拼接参考
## 用法：pyroe make-splicigenome_file gtf_file read_length out_dir
## read_lengh 是测序仪执行的测序循环数。如果您不确定，请询问您的技术人员。
## 公开可用的数据集通常在描述中包含读取长度。
Pyroe 拼接 \
${ref_dir}/fasta/genome.fa \
${ref_dir}/genes/genes.gtf \
90\
splici_rl90_ref

# 索引参考
## 用法：鲑鱼索引 -textend_txome.fa -i idx_out_dir -p num_threads
## $() 表达式在内部运行命令并将输出放在适当的位置。
## 请确保`splici_ref`文件夹中只有一个以“.fa”结尾的文件。
鲑鱼指数\
- t $(ls splici_rl90_ref/*\.fa) \
- i 鲑鱼索引 \
- p 8

```

The _splici_ index can be found in the `salmon_index` directory.

(raw-proc:example-quant)=

#### Mapping and quantification

Next, we will map the sequencing reads recorded against the _splici_ index by calling [`salmon alevin`](https://salmon.readthedocs.io/en/latest/alevin.html). This will produce an output folder called `salmon_alevin` that contains all the information we need to process the mapped reads using `alevin-fry`.

```bash
# 收集 FASTQ 文件
## 文件名排序并用空格分隔。
read1="$(find -L $fastq_dir -name "*$reads1_pat*" -type f | sort | awk '{$1=$1;print}' |粘贴 -sd' ')"
read2="$(find -L $fastq_dir -name "*$reads2_pat*" -type f | sort | awk '{$1=$1;print}' |粘贴 -sd' ')"

# 映射
## 用法：salmon alevin -i index_dir -l library_type -1 读取1_文件 -2 读取2_文件 -p num_threads -o 输出目录
## 上面定义的变量reads1和reads2是使用${}传入的。
鲑鱼素\
- i 鲑鱼索引 \
- l ISR \
- 1 ${reads1} \
- 2 ${reads2} \
- p 8 \
- o 鲑鱼_alevin \
- -chromiumV3 \
- -草图
```

Then, we execute the cell barcode correction and UMI resolution step using `alevin-fry`. This procedure involves three `alevin-fry` commands:

1. The [`generate-permit-list`](https://alevin-fry.readthedocs.io/en/latest/generate_permit_list.html) command is used for cell barcode correction.
2. The [`collate`](https://alevin-fry.readthedocs.io/en/latest/collate.html) command filters out invalid mapping records, corrects cell barcodes and collates mapping records originating from the same corrected cell barcode.
3. The [`quant`](https://alevin-fry.readthedocs.io/en/latest/quant.html) command performs UMI resolution and quantification.

```bash
# 细胞条形码校正
## 用法：alevin-frygenerate-permit-list -u CB_permit_list -d预期方向-o gpl_out_dir
## 此处，通过指定`-d fw`过滤掉映射到转录本反向互补链的读数。
alevin-fry 生成许可列表 \
- u 3M-2018 年 2 月.txt \
- d fw \
- i 鲑鱼_alevin \
- o alevin_fry_gpl

# 过滤映射信息
## 用法：alevin-fry collate -i gpl_out_dir -r alevin_map_dir -t num_threads
alevin-fry 整理 \
- i alevin_fry_gpl \
- r 鲑鱼_alevin \
- t 8

# UMI 分辨率 + 量化
## 用法：alevin-fry Quant -r 分辨率 -m txp_to_gene_mapping -i gpl_out_dir -o quant_out_dir -t num_threads
## splici_ref 文件夹中以`3col.tsv`结尾的文件将传递给 -m 参数。
## 请确保`splici_ref`文件夹中只有一个此类文件。
alevin-fry Quant -r cr 式 \
- m $(ls splici_rl90_ref/*3col.tsv) \
- i alevin_fry_gpl \
- o alevin_fry_quant \
- t 8
```

After running these commands, the resulting quantification information can be found in `alevin_fry_quant/alevin`.
Other relevant information concerning the mapping, CB correction, and UMI resolution steps can be found in the `salmon_alevin`, `alevin_fry_gpl`, and `alevin_fry_quant` folders, respectively.

In the example given here, we demonstrate using `simpleaf` and `alevin-fry` to process a 10x Chromium 3' v3 dataset.
`Alevin-fry` and `simpleaf` provide many other options for processing different single-cell protocols, including but not limited to Dropseq {cite}`raw:Macosko2015`, sci-RNA-seq3 {cite}`raw:Cao2019` and other 10x Chromium platforms.
A more comprehensive list and description of available options for different stages of processing can be found in the [`alevin-fry`](https://alevin-fry.readthedocs.io/en/latest/) and [`simpleaf`](https://github.com/COMBINE-lab/simpleaf) documentation.
`alevin-fry` also provides a [nextflow](https://www.nextflow.io/docs/latest/)-based workflow, called [quantaf](https://github.com/COMBINE-lab/quantaf), for conveniently processing many samples from a simply-defined sample sheet.

Of course, similar resources exist for many of the other raw data processing tools referenced and described throughout this section, including [`zUMIs`](https://github.com/sdparekh/zUMIs/wiki) {cite}`zumis`, [`alevin`](https://salmon.readthedocs.io/en/latest/alevin.html) {cite}`Srivastava2019`, [`kallisto|bustools`](https://www.kallistobus.tools/) {cite}`Melsted2021`, [`STARsolo`](https://github.com/alexdobin/STAR/blob/master/docs/STARsolo.md) {cite}`Kaminow2021` and [`CellRanger`](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/what-is-cell-ranger).
The [`scrnaseq`](https://nf-co.re/scrnaseq) pipeline from [`nf-core`](https://nf-co.re/) also provides a nextflow-based pipeline for processing single-cell RNA-seq data generated using a range of different chemistries and integrates several of the tools described in this section.

(raw-proc:useful-links)=

## Useful links

[Alevin-fry tutorials](https://combine-lab.github.io/alevin-fry-tutorials/) provide tutorials for processing different types of data.

[`Pyroe`](https://github.com/COMBINE-lab/pyroe) in python and [`roe`](https://github.com/COMBINE-lab/roe) in R provide helper functions for processing `alevin-fry` quantification information. They also provide an interface to the preprocessed datasets in [`quantaf`](https://combine-lab.github.io/quantaf).

[`Quantaf`](https://github.com/COMBINE-lab/quantaf) is a nextflow-based workflow of the `alevin-fry` pipeline for conveniently processing a large number of single-cell and single-nucleus data based on the input sheets. The preprocessed quantification information of publicly available single-cell datasets is available on its [webpage](https://combine-lab.github.io/quantaf).

[`Simpleaf`](https://github.com/COMBINE-lab/simpleaf) is a wrapper of the alevin-fry workflow that allows executing the whole pipeline, from making _splici_ reference to quantification as shown in the above example, using only two commands.

Tutorials for processing scRNA-seq raw data from [the galaxy project](https://galaxyproject.org/) can be found at [here](https://training.galaxyproject.org/training-material/topics/transcriptomics/tutorials/scrna-preprocessing-tenx/tutorial.html) and [here](https://training.galaxyproject.org/training-material/topics/transcriptomics/tutorials/scrna-preprocessing/tutorial.html).

Tutorials for explaining and evaluating FastQC report are available from [MSU](https://rtsf.natsci.msu.edu/genomics/technical-documents/fastqc-tutorial-and-faq.aspx), [the HBC training program](https://hbctraining.github.io/Intro-to-rnaseq-hpc-salmon/lessons/qc_fastqc_assessment.html), [Galaxy Training](https://training.galaxyproject.org/training-material/topics/sequence-analysis/tutorials/quality-control/tutorial.html) and [the QC Fail website](https://sequencing.qcfail.com/software/fastqc/).

(raw-proc:references)=

## References

```{bibliography}
:filter: docname in docnames
:labelprefix: raw
```

## Contributors

We gratefully acknowledge the contributions of:

### Authors

- Dongze He
- Avi Srivastava
- Hirak Sarkar
- Rob Patro
- Seo H. Kim

### Reviewers

- Lukas Heumos
