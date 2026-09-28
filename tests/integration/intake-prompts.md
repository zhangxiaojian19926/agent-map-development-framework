# 自然语言接入验收

维护者在授权的合成环境运行 `python3 tools/verify-live --scenario intake --host codex --target NEW_PATH --allow-live`；另以独立目标和 `--host claude` 重复。无授权不创建目录，缺宿主/认证记 NOT_RUN，不用 stub 或 Codex替代另一个宿主。

实际发给宿主的请求只含：初始化意图、BOOTSTRAP位置、PROJECT-START.md位置、目标/启动区位置，以及本次合成范围权限。输入分别是三个同basename来源的中文名称键值对和无URL新需求；不预制 JSON、内部 ID、hash或执行步骤。新工程未获得设计决定时，正确交付是完整设计草案/dossier及NEEDS_DESIGN_APPROVAL/PARTIAL，不是擅自批准后COMPLETE。

独立验收核对真实来源/name/path/HEAD、用户文件保留、当前会话分析接收、doctor各层状态，完整原始轨迹保存在验证目录 evidence；不得把只读解析成功当成建图完成。宿主返回成功但文件不满足仍记 FAILED。

探针分别比较源与克隆的实际HEAD和源码hash，并重新校验dossier；同remote但错HEAD、内容被改或仅占位资料均拒绝。语义正确性、运行和跨宿主恢复分别记录，机器schema通过不代替人工/Agent语义复核。非Codex验收还必须独立确认没有执行codex，普通离线PATH隔离测试不能代替真实宿主轨迹。

跨宿主恢复单独执行：第一宿主完成部分初始化后结束；第二宿主只收到相同启动区与“继续初始化”和当前权限。核对成功模块 HEAD及文件指纹不变、未重复clone、无发布；状态保留 NOT_RUN直至真实完成。整段宿主运行每次最多20分钟。
