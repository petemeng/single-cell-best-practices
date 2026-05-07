# 术语表

```{glossary}
Adapter sequences
    在测序文库制备过程中连接在 DNA 或 RNA 片段末端的短合成 DNA 或 RNA 序列。
    这些接头对于将片段结合到流动槽并实现扩增和测序至关重要。
    然而，如果测序后未修剪接头，它们可能出现在读段中，可能干扰比对和下游分析。

Algorithm
    一组预定义的解决问题的指令。

Annotation
    为原始数据添加标签以提供上下文并使其可解释。
    例如，基因注释用功能、位置和关联蛋白质等信息标记基因。
    细胞注释基于类型、状态或功能对细胞进行分类。
    这些只是几个例子。
    还有更多注释生物数据的方式（例如，基于批次、疾病、性别等）。

AnnData
    一个用于处理带注释数据矩阵的 Python 包，常用于单细胞和其他组学分析。
    它提供了一种高效的数据存储方式，将数据存储为矩阵，其中行（观测）和列（特征）可以具有关联的元数据。
    [AnnData](https://anndata.readthedocs.io/en/latest/index.html) 支持切片、子集化，以及以 H5AD 和 Zarr 等格式保存到磁盘。

BAM
    BAM 文件是 SAM（Sequence Alignment/Map）文件的二进制压缩版本，存储测序读段比对到参考基因组的信息。
    它们包含与 {term}`SAM` 文件相同的信息——包括读段序列、质量分数和比对位置——但以更节省空间的格式存储，从而实现更快的处理和减少存储需求。

Amplification bias
    在 DNA 或 RNA 扩增（如 PCR）过程中发生的一种扭曲，其中某些序列比其他序列更有效地被复制。这可能导致原始遗传材料的不均匀或不准确表示，影响测序或基因表达分析等实验的结果。

Barcode
    短的 DNA 条形码片段（"标签"），用于识别源自同一细胞的读段。
    在原始数据处理步骤中，读段随后按其条形码分组。

Batch effect
    实验中导致数据集分布偏移的技术混淆因素。
    如果批次效应的原因与实验中感兴趣的结果相关，通常会导致不准确的结论，应予以考虑（通常需要消除）。

Benchmark
    根据预定义的指标，对若干工具的性能进行的（独立）比较。

Bulk RNA sequencing
    与单细胞测序相反，批量测序测量多个细胞的平均表达值。因此，分辨率会丢失，但批量测序通常更便宜、更省力且分析更快。

Cell
    生命的基本单位，由细胞质和包裹其的细胞膜组成，含有蛋白质和核酸等生物分子。
    细胞获得特定功能，转变为不同类型，分裂并通信以维持生物体。
    研究细胞结构、活动和相互作用可以深入了解基因表达动态、细胞轨迹、发育谱系和疾病机制。

Cell type annotation
    根据 {term}`cell type <Cell type>` 为细胞 {term}`clusters <Cluster>` 分组标注标签的过程。
    通常基于细胞类型特异性标记基因、使用分类器自动进行或通过与参考数据集比对来完成。

Cell type
    共享共同形态或表型特征的细胞。

Cell state
    细胞可以根据 {term}`cell type <Cell type>` 或其他细胞状态（如细胞周期、扰动状态或其他特征）进行注释。

Chromatin
    DNA 和蛋白质的复合物，有效地将 DNA 包装在细胞核内，并参与调控基因表达。

Codon
    三个核苷酸的序列，对应蛋白质合成中的特定氨基酸或起始/终止信号。
    密码子是遗传密码的基本单位，决定遗传信息如何翻译成蛋白质。

CpG
    一种 DNA 序列，其中胞嘧啶 (C) 后面是鸟嘌呤 (G)，沿 5' &rarr; 3' 方向，通过磷酸二酯键连接。
    CpG 位点通常存在于基因启动子附近称为 CpG 岛的簇中。
    未甲基化的 CpG 位点与基因激活相关，而甲基化的 CpG 位点则可能导致基因抑制。

Cluster
    一组具有相似性的群体或数据点。
    在单细胞领域，聚类通常共享共同的功能或标记基因表达，用于注释（参见 {term}`cell type annotation <Cell type annotation>`）。

Complementary DNA (cDNA)
    由逆转录酶以 RNA 为模板合成的 DNA。
    cDNA 常用于 RNA-seq 文库制备，因为它比 RNA 更稳定，并允许捕获的转录本被扩增和测序以进行基因表达分析。

Demultiplexing
    使用 {term}`barcodes <Barcode>` 确定哪些测序读段属于哪个细胞的过程。

Directed graph
    有向图（或 digraph）是由一组节点（顶点）通过边（弧）连接的图，其中每条边都有方向，表示节点之间的单向关系。

DNA
    DNA 是脱氧核糖核酸（Deoxyribonucleic acid）的缩写。
    它是存储遗传信息和蛋白质合成指令的有机化学物质。
    DNA 被转录为 {term}`RNA`。

Doublets
    在基于液滴的实验中获得的读段可能被错误地关联到单个细胞，而实际 RNA 表达源自两个或更多细胞（双联体）。

Downstream analysis
    在原始数据初步处理之后进行的数据分析阶段。
    在 scRNA-seq 的背景下，这包括标准化、整合、过滤、细胞类型鉴定、轨迹推断和研究表达动态等任务。

Driver genes
    在生物过程中主动控制或"驱动"细胞从一种状态转变为另一种状态的基因。
    与仅用于识别细胞类型的标记基因不同，驱动基因在分支点的命运决定中起功能性作用。

Dropout
    在一个细胞中观测到但在同一 {term}`cell type <Cell type>` 的其他细胞中未观测到的低表达基因。
    Dropout 的原因通常是细胞中 {term}`mRNA <Messenger RNA (mRNA)>` 表达量低以及 mRNA 表达的普遍随机性。
    Dropout 是 scRNA-seq 数据稀疏的原因之一。

Drop-seq
    一种 scRNA-seq 实验方案，将细胞分离到纳升级大小的水性液滴中，实现大规模分析。

Edit distance
    编辑距离（通常称为 Levenshtein 距离）衡量将一个字符串转换为另一个字符串所需的最少操作数（替换、插入、删除）。

Embedding
    将复杂对象（如单词、蛋白质或基因）表示为数值向量的一种方式，以便计算机更容易分析。

FASTQ
    以 FASTQ 格式保存的测序读段。
    FASTQ 文件以 4 行格式存储 DNA/RNA 序列及其对应的质量分数：标识符、序列、可选描述和以 ASCII 字符编码的质量分数。
    然后使用 FASTQ 文件比对到感兴趣的参考基因组，以获得细胞的基因计数。

Flowcell
    测序平台中用于对 DNA 或 RNA 片段进行测序的消耗性设备。
    它由带有通道或泳道的玻璃或聚合物表面组成，表面涂有寡核苷酸，用于捕获和固定 DNA 或 RNA 片段。
    在测序过程中，这些片段被扩增成簇，通过检测核苷酸掺入时发出的荧光信号来确定其序列。
    流动槽通过允许同时测序数百万个片段来实现高通量测序。

Gene expression matrix
    一个细胞（条形码）×基因（scverse 生态系统）或基因×细胞（条形码）矩阵，在单元格中存储计数值。

Hamming distance
    衡量两个等长字符串在多少个位置上不同的度量。
    常用于测序数据中的错误检测和校正，包括条形码校正。

Imputation
    用通常为人工值的值替换缺失值。

Indrop
    一种基于液滴的 scRNA-seq 实验方案。

Library
    也称测序文库。带有连接测序接头的 DNA 片段池。

Modalities
    在单细胞水平上测量的不同类型的生物学信息。
    包括基因表达、染色质可及性、表面蛋白、免疫受体序列和空间组织。
    组合这些模态可以更全面地理解细胞身份、功能和相互作用。

Locus
    基因组或转录组上特定序列或遗传特征所在的特定位置或区域。
    在测序中，基因座指读段或片段的潜在来源，如基因、外显子或基因间区域。
    准确定位基因座对于读段比对和理解数据的基因组或转录组背景至关重要。

Messenger RNA (mRNA)
    从基因转录而来的核苷酸序列，作为蛋白质的蓝图。

Marker gene
    其表达用作特定细胞类型、生物过程或细胞状态指标的基因。
    标记基因常用于单细胞和批量转录组学中，基于细胞的功能或身份来识别或分类细胞。

MuData
    一个用于多模态注释数据矩阵的 Python 包，建立在 {term}`AnnData` 之上。
    是 scverse 生态系统中多模态数据的主要数据结构。

Muon
    scverse 提供的用于 Python 中多模态单细胞分析的 Python 包。

Negative binomial distribution
    一种离散概率分布，用于建模在一系列独立同分布的伯努利试验中，在指定数量的失败之前获得成功的次数。

PCR
    聚合酶链式反应（PCR）是一种扩增序列以产生数十亿拷贝的方法。
    PCR 需要引物（短的合成 {term}`DNA` 片段）来选择要扩增的基因组片段，随后进行多轮 {term}`DNA` 合成以扩增目标片段。

Pipeline
    通常也称为工作流。
    一组预先指定的步骤，通常按顺序执行。

Poisson distribution
Poisson distributed
    离散概率分布，表示在固定的时间或空间间隔内，以已知的恒定平均速率独立发生的事件的指定数量的概率。

Principal component analysis (PCA)
    一种统计方法，通过减少变量数量同时保留数据中的主要模式来简化复杂数据集。
    它将高维数据投影到正交轴（主成分）上，按解释的方差量排序。

Promoter
    蛋白质（如 RNA 聚合酶和转录因子）结合的 DNA 序列，用于启动和控制转录。

Pseudotime
    潜在且因此不可观测的维度，反映细胞在转变过程中的进展。
    伪时间通常与真实时间事件相关，但不一定相同。

RNA
    核糖核酸（RNA）是存在于所有活细胞中的单链核酸，编码并调控基因表达。
    与 DNA 不同，RNA 可以是高度动态的，充当信使（{term}`mRNA <Messenger RNA (mRNA)>`）携带遗传指令，结构或催化组分（rRNA、snRNA），或基因表达调控因子（miRNA、siRNA、lncRNA）。
    RNA 在转录、翻译和细胞响应中起核心作用，使其对于理解基因调控、发育和疾病至关重要。

RNA velocity
    RNA 速度通过比较单细胞 RNA 测序数据中未剪接（前体 {term}`mRNA <Messenger RNA (mRNA)>`）与剪接（成熟）mRNA 转录本的比率来衡量基因表达的变化速率。
    该比率提供了基因是否正在被积极转录（表达增加）或降解（表达减少）的洞察，使研究人员能够预测细胞的未来状态。
    这一概念利用了前体 mRNA 信号指示新转录而成熟 mRNA 水平反映稳态表达的事实，从而能够推断细胞轨迹和发育动力学。

SAM
    SAM（Sequence Alignment/Map）文件是制表符分隔的文本文件，存储测序比对数据，显示测序读段如何比对到参考基因组。
    SAM 文件中的每一行包含单条读段比对的信息，包括读段序列、碱基质量分数、比对位置和比对质量。

Scanpy
    scverse 提供的用于 Python 中单细胞分析的 Python 包。

Scverse
    生命科学领域基础单细胞工具的联合体，维护着 scanpy、muon 和 scvi-tools 等计算分析工具。
    参见：https://scverse.org/

Sequencing
    测序是解密 DNA 核苷酸顺序的过程。

Signal-to-noise ratio
    衡量信号相对于背景噪声的清晰度的指标。
    在测序中，信号代表从被测序的 DNA 或 RNA 分子中获得的可检测信息，而噪声包括可能模糊或扭曲真实数据的随机错误或不需要的信号。
    高信噪比（SNR）表示信号相对于噪声是强且可靠的，从而获得更好的数据质量。
    相反，低 SNR 意味着噪声可能干扰或降低测序结果的准确性。

Sparse data
    指数据大部分为零，很少测量到其他值（[稀疏数据 vs. 缺失数据](https://medium.com/biased-algorithms/sparse-data-vs-missing-data-38bc2c7af7c6)）。
    这在基因表达数据中很常见，其中许多基因在大多数细胞中不表达。

Sparse matrix
    一种存储 {term}`sparse data` 的方式。
    它不保留所有零值，只保存非零值及其位置，节省空间并使计算更快。
    对于大多数值为空的大型数据集（如基因表达数据）非常有用。

Spike-in RNA
    已知序列和数量的 RNA 转录本，用于校准 RNA-seq 中 RNA 杂交步骤的测量。

Splice Junctions
    在 RNA 剪接过程中，内含子被移除、外显子被连接在一起形成成熟 RNA 转录本的位置。
    这些连接点发生在特定的核苷酸序列处，对于功能性 {term}`mRNA <Messenger RNA (mRNA)>` 的正确组装至关重要。

Trajectory inference
    也称为伪时间排序。
    通过按相似性或其他方式对细胞进行排序来恢复动态过程的计算方法。

Unique Molecular Identifier (UMI)
    一种特殊类型的分子条形码，为样本文库中的每个分子进行唯一标记。
    例如，这使得能够估计 PCR 重复率（参见 {term}`amplification bias <Amplification bias>`），从而实现错误校正并提高准确性。

Untranslated Region (UTR)
    {term}`mRNA <Messenger RNA (mRNA)>` 转录本中被转录但不翻译成蛋白质的区段。
    UTR 位于编码序列的两端。
```
