# 现有技术

单细胞分析已经从一个感兴趣的利基领域发展成为一个成熟的研究领域。
因此，我们当然不是第一个出版有关该主题的书籍，也不是第一个提供指南和教程的人。
在接下来的部分中，我们回顾了两项旨在教授单细胞分析的著名且正在进行的举措，强调它们与本书的相似之处和不同之处。

(introduction-prior-art-key-takeaway-1)=

## Bioconductor OSCA 和 OSTA 书籍

Orchestrating Single-Cell Analysis 和 Bioconductor (Bioconductor OSCA) {cite}`osca`，可在 https://bioconductor.org/books/release/OSCA/, 在线获取，是一本在线书籍，旨在教授使用基于 R 的语言分析单细胞 {term}`RNA`-{term}`Sequencing`(scRNA-seq) 数据的常见工作流程Bioconductor 生态系统 {cite}`pa:Huber2015`。
附带的同名论文 {cite}`Amezquita2020`提供了使用 Bioconductor 进行单细胞分析的概述，而在线书籍则提供了更深入的介绍，包括详细的解释和广泛的代码示例。

The OSCA 书对基本 scRNA-seq 分析的处理非常全面，提供了清晰的解释和详细的工作流程示例。
然而，它并没有扩展到其他单细胞组学，例如单细胞 ATAC-seq (scATAC-seq)。
空间转录组学在补充书 Orchestrating Spatially-Resolved Transcriptomics Analysis 和 Bioconductor (Bioconductor OSTA) 中单独讨论，可在 https://lmweber.org/OSTA-book/. 获取

由于这两本书都是针对 Bioconductor 生态系统量身定制的，因此它们专门使用 Bioconductor 中提供的工具。
虽然这些工具非常有效，但正如书籍本身所承认的那样，它们可能并不总是为每次分析提供最佳解决方案。
总体而言，Bioconductor 书籍特别适合具有 R 基础知识和强大生物学背景、希望学习如何在 Bioconductor 框架内分析单细胞和空间转录组数据的个人。

(introduction-prior-art-key-takeaway-2)=

## 当前单细胞 RNA-seq 分析的最佳实践：教程

单细胞中的 Current Best Practices {term}`RNA`-Seq Analysis：Malte Lücken 的教程 {cite}`pa:Lücken2019`和 Fabian Theis 介绍了 scRNA-seq 分析的最佳实践。
其主要贡献不仅在于审查潜在的分析步骤，还在于基于独立基准推荐最佳实践。
当无法获得具体的最佳实践指南时，作者会提供分析方法的一般建议。
关注独立基准的基本理念极大地启发了我们的工作。
Haber 等人的 [example analysis of mouse intestinal epithelium regions](https://github.com/theislab/single-cell-tutorial/) 对本文进行了补充。 {cite}`pa:Haber2017`。

与 Bioconductor OSCA 相比，本文及其相关分析不受特定工具生态系统的限制，为所涵盖的主题范围提供了更广泛的视角。
然而，随附的示例分析缺乏初学者友好性，并且已经过时。
与 Bioconductor OSCA 类似，Lücken & Theis 不涉及 RNA 速度、空间转录组学或多组学等较新的发展。

尽管存在这些限制，我们强烈推荐本文作为对该领域的有价值的介绍，并作为 scRNA-seq 分析中初始最佳实践的指南。
本书中的章节以最新的最佳实践为基础，提供了该领域的最新观点。此外，本书对工作流程进行了更详细的解释，为读者提供了有效应用这些方法所需的背景信息。
我们建议不要依赖论文中提供的示例案例研究，而是鼓励读者探索本书中的详细章节，以获得更全面和最新的理解。

## 参考

```{bibliography}
:filter: docname in docnames
:labelprefix: pa
```
