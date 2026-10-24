# 逆向工具版本

普通工程初始化不安装、不调用这些工具。只有 `reverse` 授权后的集中安装才读取本页和 `tools/framework_core/rea-tools.lock.json`。没有校验值的条目不会下载。

| 工具 | 固定版本 | 系统 |
|---|---|---|
| rea-agents | 6.7.0 | macOS、Linux |
| Ghidra | 12.1.4 | macOS、Linux |
| Eclipse Temurin JDK | 21.0.13+9 | macOS、Linux。校验值未写入 lock 之前不下载 |
| JADX | 1.5.6 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Apktool | 3.0.3 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Rizin | 0.9.1 | macOS、Linux。校验值未写入 lock 之前不下载 |
| WABT | 1.0.42 | macOS、Linux。校验值未写入 lock 之前不下载 |
| Android platform-tools | 实现时锁定的官方包 | macOS、Linux。校验值未写入 lock 之前不下载 |
| pwntools、Unblob、TShark 4.x、sigrok-cli 0.7.2 | Linux 专用 | macOS 返回 HOST_UNSUPPORTED，不下载 |

Ghidra 使用已公布的 SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`。不安装 Hopper、IDA 或 JEB。Node.js 只检测，壳不安装。
