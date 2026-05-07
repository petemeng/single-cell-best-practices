本书使用 [lamindb](https://github.com/laminlabs/lamindb) 来存储、共享和加载使用 [theislab/sc-best-practices instance](https://lamin.ai/theislab/sc-best-practices) 的数据集和笔记本。
我们承认 [Lamin Labs](https://lamin.ai/) 提供免费托管。

1. **安装lamindb**
   - 安装 lamindb Python 包：

   ```bash
   pip install lamindb
   ```

2. **可选择创建一个 lamin 帐户**
   - 按照 [the instructions](https://docs.lamin.ai/setup#sign-up-log-in) 注册并登录

3. **验证您的设置**
   - 运行`lamin connect`命令：

   ```python
   import lamindb as ln

   ln.Artifact.connect("theislab/sc-best-practices").df()
   ```

   您现在应该可以看到最多 100 个存储的数据集。

4. **访问数据集（工件）**
   - 搜索 [Artifacts page](https://lamin.ai/theislab/sc-best-practices/artifacts) 上的数据集
   - 加载Artifact和相应的对象：

   ```python
   import lamindb as ln
   af = ln.Artifact.connect("theislab/sc-best-practices").get(key="key_of_dataset", is_latest=True)
   obj = af.load()
   ```

   该对象现在可以在内存中访问并准备好进行分析。
   调整`ln.Artifact.connect("theislab/sc-best-practices").get("SOMEIDXXXX")`后缀以获得相应的版本。

5. **访问笔记本（转换）**
   - 在 [Transforms page](https://lamin.ai/theislab/sc-best-practices/transforms) 上搜索笔记本
   - 加载笔记本：

   ```bash
   lamin load <notebook url>
   ```

   这会将笔记本下载到当前工作目录。
   与`Artifacts`类似，您可以调整后缀 ID 以获取旧版本。
