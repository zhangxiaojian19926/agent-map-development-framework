# 工程启动单模板（不要把整个模板作为输入）

选择下面一种，将代码块中的内容保存为你自己的 PROJECT-START.md。文件放在目标工程外的私有工作目录，不放公共框架仓库。不填写执行配置、内部 ID 或批准 hash。

## 已有工程：任意数量的命名模块

```text
# 工程启动单
项目：设备助手
## 模块仓库
设备端 = https://example.com/team/device.git
服务端 = git@example.com:team/service.git
管理界面 = https://example.com/team/console.git
```

也可只提供多行 `模块名称 = URL`；省略项目名时用已确认目标目录名。示例 URL 必须换成你自己的来源。默认使用远程实际默认分支。需要指定来源时在模块区块后另加：

```text
## 来源版本
设备端 = branch:release/2.x
服务端 = tag:v1.0
```

## 全新工程：不需要仓库

```text
# 工程启动单
项目：家庭任务助手
目标：在本机新增、列出和完成任务，暂不部署。
仓库：暂无
```

把这份输入和框架 BOOTSTRAP.md 的位置给 Coding Agent，说“初始化工程”。目标目录已明确就直接接入；尚不明确时 Agent 只询问必要位置。仓库凭据使用宿主安全认证，不写在输入或 URL 中。
