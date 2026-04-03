# Phase 4: Code Quality

## 目标
提升代码质量：类型约束、文件处理优化、代码整洁

## 任务

### 4.1 Todo.quadrant 使用 Enum 替代魔法数字
- **文件**: `app/models.py`, `app/todo/utils.py`, `app/todo/routes.py`
- **问题**: 1-4 使用注释说明，容易出错
- **修复**:
  ```python
  from enum import IntEnum
  
  class Quadrant(IntEnum):
      DO_FIRST = 1      # 紧急且重要
      SCHEDULE = 2      # 不紧急但重要
      DELEGATE = 3      # 紧急但不重要
      ELIMINATE = 4     # 不紧急也不重要
  ```
  - 模型中使用 `Quadrant` 类型
  - 路由验证使用 `Quadrant` 成员

### 4.2 文件导入大小检查优化
- **文件**: `app/admin/routes.py`
- **问题**: `MAX_FILE_SIZE + 1` 读取后才检查，浪费内存
- **修复**:
  ```python
  f.seek(0, 2)  # 移到末尾
  size = f.tell()
  f.seek(0)  # 回到开头
  if size > MAX_FILE_SIZE:
      skipped.append(f"{filename}（文件超过 512KB）")
      continue
  # 安全读取
  content = f.read(MAX_FILE_SIZE).decode('utf-8')
  ```

### 4.3 移除 `app/db.py` 废弃模块
- **文件**: `app/db.py`
- **问题**: 注释标注 legacy，但仍存在造成混淆
- **修复**:
  - 确认无引用后删除
  - 或移动到 `app/legacy/` 目录

### 4.4 清理调试 print 语句
- **文件**: `app/todo/routes.py`
- **问题**: 多处 `print()` 用于调试，生产不应有
- **修复**:
  - 移除所有调试 print
  - 使用 `current_app.logger.debug()` 替代必要的调试日志

## 验证标准
- [ ] `Quadrant.SCHEDULE == 2` 可正常使用
- [ ] 文件上传时内存占用恒定
- [ ] `app/db.py` 已删除或移动
- [ ] 代码中无 `print(` 调试语句

## 依赖
阶段 1, 2, 3 完成

## 预计工时
1-2 小时
