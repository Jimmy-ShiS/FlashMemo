# clash-for-linux Skill

管理 Linux 上的 Clash 代理服务。基于 clash-for-linux-install 安装。

## 安装位置

- **安装目录**: `/home/jimmy/Softwares/clashctl`
- **配置文件**: `/home/jimmy/Softwares/clashctl/resources/config.yaml`

## 前置要求

所有命令需要在 **root** 权限下执行。必须使用 `sudo su - root -c "source ... && 命令"` 格式。

## 命令格式

```bash
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && 命令"
```

## 命令列表

### 开启/关闭代理

```bash
# 开启代理（同时启动内核 + 设置系统代理）
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashon"

# 关闭代理（同时停止内核 + 清除系统代理）
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashoff"
```

### 状态查询

```bash
# 查看内核运行状态
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashctl status"
```

### Web 控制面板

```bash
# 打开 Web 控制台（默认端口 9090）
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashui"

# 设置/查看访问密钥
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsecret mysecret"   # 设置密钥
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsecret"           # 查看当前密钥
```

访问地址：`http://<IP>:9090/ui`

### 订阅管理

```bash
# 查看订阅列表
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub ls"

# 添加订阅
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub add <订阅URL>"

# 使用指定订阅
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub use <id>"

# 更新订阅
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub update <id>"
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub update --auto"

# 删除订阅
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub del <id>"

# 查看订阅日志
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashsub log"
```

### Tun 模式

```bash
# 查看 Tun 状态
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashtun"

# 开启 Tun 模式
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashtun on"

# 关闭 Tun 模式
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashtun off"
```

### Mixin 配置

```bash
# 查看 Mixin 配置
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashmixin"

# 编辑 Mixin 配置
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashmixin -e"

# 查看原始订阅配置
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashmixin -c"

# 查看运行时配置
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashmixin -r"
```

### 升级内核

```bash
# 升级内核
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashupgrade"
sudo su - root -c "source /home/jimmy/Softwares/clashctl/scripts/cmd/clashctl.sh && clashupgrade -v"
```

## 注意事项

1. 所有命令必须使用 `sudo su - root -c "source ... && 命令"` 格式
2. Web 面板默认端口 9090，需确保防火墙放行
3. 首次使用需要添加订阅：`clashsub add <URL>`
