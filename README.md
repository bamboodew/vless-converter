# VLESS to Clash.Meta Converter

这是一个 Python 脚本，用于将包含 VLESS 链接的文本文件批量转换为 Clash.Meta 客户端兼容的 YAML配置文件。

## ✨ 功能

-   **批量转换**：从文本文件读取多个 VLESS 链接。
-   **智能命名**：自动从链接的 `#` 部分提取节点名称。
-   **多协议支持**：兼容 `ws` (WebSocket) 和 `grpc` 传输协议。
-   **命令行操作**：通过命令行参数指定输入和输出文件，方便集成。

## 🚀 使用方法

1.  **准备节点文件**：
    创建一个名为 `nodes.txt` (或通过 `-i` 参数指定其他名称) 的文本文件，每行粘贴一个 VLESS 链接。

    ```txt
    vless://uuid@server:port?type=ws&path=/path&host=example.com#Node_1
    vless://uuid@server:port?type=grpc&serviceName=my.service#Node_2
    ```

2.  **运行脚本**：
    在终端中执行以下命令：

    ```bash
    python vless_txt_to_yaml.py
    ```

    或者，指定自定义的输入和输出文件：

    ```bash
    python vless_txt_to_yaml.py -i my_links.txt -o my_config.yaml
    ```

3.  **完成**：
    脚本将生成一个名为 `clash_meta_from_txt.yaml` (或通过 `-o` 参数指定的名称) 的配置文件，可以直接在 Clash.Meta 客户端中使用。