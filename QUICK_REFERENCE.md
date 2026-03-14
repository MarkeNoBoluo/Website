# Raspberry Pi开发 - 快速参考

## 网络变更后的快速恢复

### 1. 找到新IP地址
```bash
# 方法A: 使用发现脚本
python find_raspberry_pi.py

# 方法B: 查看路由器管理界面
# 访问 http://192.168.1.1，查找"RaspberryPi-wddkxg"
```

### 2. 一键更新所有配置
```bash
update_all_connections.bat 192.168.1.105
```

### 3. 或分别更新
```bash
# 更新SSH配置
update_pi_ip.bat 192.168.1.105

# 更新git配置
update_git_remote.bat 192.168.1.105
```

## 日常开发命令

### SSH连接
```bash
ssh raspberrypi      # 主要别名
ssh pi              # 简短别名
ssh wddkxg@IP地址   # 直接连接
```

### Git操作
```bash
git status           # 查看状态
git add .            # 添加文件
git commit -m "消息"  # 提交更改
git push origin develop  # 部署到树莓派
```

### 服务管理
```bash
# 在树莓派上执行
sudo systemctl status blog.service  # 检查服务状态
sudo systemctl restart blog.service # 重启服务
sudo journalctl -u blog.service -n 20  # 查看日志
```

## 故障排查

### SSH连接失败
```bash
# 测试连接
ssh -v raspberrypi

# 检查配置
cat ~/.ssh/config

# 验证密钥
ssh-keygen -y -f ~/.ssh/id_rsa_raspberry
```

### Git推送失败
```bash
# 测试git连接
git ls-remote origin

# 更新远程URL
git remote set-url origin ssh://wddkxg@新IP/home/wddkxg/blog.git
```

### 网站无法访问
```bash
# 检查服务
ssh raspberrypi "sudo systemctl status nginx blog.service"

# 测试HTTP访问
ssh raspberrypi "curl -I http://localhost:8080/"
```

## 文件位置

- SSH配置: `~/.ssh/config`
- SSH密钥: `~/.ssh/id_rsa_raspberry`
- Git仓库: `E:\Website\`
- 部署脚本: `update_*.bat`, `find_raspberry_pi.py`

## 紧急恢复

如果完全无法连接：
1. **物理访问树莓派**（如果有显示器）：
   ```bash
   hostname -I  # 获取IP
   sudo systemctl restart ssh  # 重启SSH服务
   ```

2. **重置网络**：
   ```bash
   sudo dhclient -r  # 释放IP
   sudo dhclient     # 获取新IP
   ```

3. **设置静态IP**（避免变化）：
   ```bash
   sudo nano /etc/dhcpcd.conf
   # 添加静态IP配置
   ```

---
*保持连接，快乐开发！*