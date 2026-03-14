# SSH连接配置 - Raspberry Pi开发环境

## 当前配置状态

✅ **SSH密钥认证已配置**
- 密钥文件: `~/.ssh/id_rsa_raspberry`
- 公钥已添加到树莓派的 `~/.ssh/authorized_keys`
- 无密码连接可用

✅ **SSH配置文件已优化**
- 别名配置: `ssh raspberrypi` 或 `ssh pi`
- 自动使用正确密钥
- 连接超时和保活设置

## 网络变更时的连接方法

### 方法1：使用更新脚本（推荐）
```bash
# 运行Python发现脚本
python find_raspberry_pi.py

# 或直接使用批处理脚本
update_pi_ip.bat 192.168.1.105
```

### 方法2：手动更新SSH配置
编辑 `~/.ssh/config` 文件，更新以下位置的IP地址：
```ssh-config
Host raspberrypi
  HostName 192.168.42.47  # ← 修改这里的IP

Host pi
  HostName 192.168.42.47  # ← 修改这里的IP
```

### 方法3：直接使用IP连接
```bash
ssh wddkxg@新IP地址
```

## 快速参考命令

### 连接命令
```bash
# 使用别名（需正确配置IP）
ssh raspberrypi
ssh pi

# 直接使用IP
ssh wddkxg@192.168.1.105

# 带端口号（如果不是默认22端口）
ssh -p 22 wddkxg@192.168.1.105
```

### 获取树莓派IP地址的方法
1. **树莓派本地查看**（如果有显示器）：
   ```bash
   hostname -I
   ip addr show
   ```

2. **路由器管理界面**：
   - 访问 `http://192.168.1.1`（或路由器IP）
   - 查看"已连接设备"、"DHCP客户端列表"
   - 寻找主机名 `RaspberryPi-wddkxg`

3. **网络扫描**（需安装nmap）：
   ```bash
   nmap -sn 192.168.1.0/24
   ```

4. **使用提供的发现脚本**：
   ```bash
   python find_raspberry_pi.py
   ```

## 故障排除

### 无法连接
1. **检查服务状态**：
   ```bash
   # 在树莓派上检查
   sudo systemctl status ssh
   ```

2. **检查防火墙**：
   ```bash
   sudo ufw status
   sudo iptables -L
   ```

3. **验证密钥权限**：
   ```bash
   chmod 600 ~/.ssh/id_rsa_raspberry
   chmod 644 ~/.ssh/id_rsa_raspberry.pub
   chmod 700 ~/.ssh
   ```

4. **调试SSH连接**：
   ```bash
   ssh -v raspberrypi
   ```

### IP地址频繁变化
**解决方案**：在树莓派上设置静态IP
```bash
# 编辑网络配置
sudo nano /etc/dhcpcd.conf

# 添加（根据网络调整）：
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

## 自动化部署集成

当前git远程仓库配置：
```bash
git remote -v
# origin  ssh://wddkxg@192.168.42.47/home/wddkxg/blog.git
```

**网络变更后的git操作**：
1. 更新SSH配置中的IP地址
2. 更新git远程URL（如果需要）：
   ```bash
   git remote set-url origin ssh://wddkxg@新IP/home/wddkxg/blog.git
   ```

## 文件说明

- `find_raspberry_pi.py` - Python IP发现脚本
- `update_pi_ip.bat` - Windows批处理更新脚本
- `~/.ssh/config` - SSH配置文件
- `~/.ssh/id_rsa_raspberry` - SSH私钥
- `~/.ssh/id_rsa_raspberry.pub` - SSH公钥

## 最佳实践

1. **定期备份SSH配置**：
   ```bash
   cp ~/.ssh/config ~/.ssh/config.backup.$(date +%Y%m%d)
   ```

2. **测试连接性**：
   ```bash
   ssh raspberrypi echo "Connection test $(date)"
   ```

3. **记录IP地址**：
   - 记录路由器分配给树莓派的IP
   - 或设置静态IP避免变化

4. **多网络环境准备**：
   - 家庭网络：192.168.1.x
   - 工作网络：192.168.0.x
   - 手机热点：192.168.42.x
   - 准备多个SSH配置节备用

---
*最后更新: 2026-03-13*