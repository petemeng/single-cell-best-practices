1. **安装conda**：
   - 创建环境之前，请确保您的系统上已安装 [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)。

2. **保存yml内容**：
   - 将 yml 选项卡中的内容复制到名为`environment.yml`的文件中。

3. **创建环境**：
   - 打开终端或命令提示符。
   - 运行以下命令：
     ```bash
     conda env create -f environment.yml
     ```

4. **激活环境**：
   - 创建环境后，使用以下命令激活它：
     ```bash
     conda activate <environment_name>
     ```
   - 将`<environment_name>`替换为`environment.yml`文件中指定的名称。在 yml 文件中，它将如下所示：
     ```yaml
     name: <environment_name>
     ```

5. **验证安装**：
   - 通过运行以下命令检查环境是否已成功创建：
     ```bash
     conda env list
     ```
