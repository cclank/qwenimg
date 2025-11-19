#!/bin/bash

# 备份当前的示例数据（数据库和图片）

echo "📦 备份 QwenImg 示例数据"
echo ""

# 创建备份目录
BACKUP_DIR="demo_data_backup"
mkdir -p "$BACKUP_DIR"

# 1. 导出数据库中最新的5条已完成任务
echo "1️⃣ 导出数据库记录..."
sqlite3 backend/qwenimg.db <<EOF > "$BACKUP_DIR/sample_tasks.sql"
.mode insert generation_tasks
SELECT * FROM generation_tasks 
WHERE status='completed' 
ORDER BY created_at DESC 
LIMIT 5;
EOF

if [ -f "$BACKUP_DIR/sample_tasks.sql" ]; then
    echo "✅ 数据库记录已导出到 $BACKUP_DIR/sample_tasks.sql"
else
    echo "❌ 数据库记录导出失败"
    exit 1
fi

# 2. 复制对应的图片文件
echo ""
echo "2️⃣ 复制图片文件..."

# 创建图片目录
mkdir -p "$BACKUP_DIR/outputs"

# 从SQL文件中提取图片路径并复制
COPIED_COUNT=0
while IFS= read -r line; do
    # 提取outputs路径
    if [[ $line =~ /outputs/([^\"]+\.png) ]]; then
        IMAGE_FILE="${BASH_REMATCH[1]}"
        if [ -f "backend/outputs/$IMAGE_FILE" ]; then
            cp "backend/outputs/$IMAGE_FILE" "$BACKUP_DIR/outputs/"
            echo "  ✅ $IMAGE_FILE"
            ((COPIED_COUNT++))
        fi
    fi
done < "$BACKUP_DIR/sample_tasks.sql"

echo ""
echo "✅ 已复制 $COPIED_COUNT 张图片"

# 3. 创建恢复脚本
echo ""
echo "3️⃣ 创建恢复脚本..."

cat > "$BACKUP_DIR/restore.sh" << 'RESTORE_SCRIPT'
#!/bin/bash

# 恢复示例数据

echo "🔄 恢复 QwenImg 示例数据"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 复制图片文件
echo "1️⃣ 复制图片文件..."
if [ -d "$SCRIPT_DIR/outputs" ]; then
    mkdir -p ../backend/outputs
    cp -v "$SCRIPT_DIR/outputs/"* ../backend/outputs/
    echo "✅ 图片文件已复制"
else
    echo "❌ 未找到图片文件"
    exit 1
fi

# 2. 导入数据库记录
echo ""
echo "2️⃣ 导入数据库记录..."
if [ -f "$SCRIPT_DIR/sample_tasks.sql" ]; then
    # 激活虚拟环境
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
    fi
    
    # 导入数据
    sqlite3 ../backend/qwenimg.db < "$SCRIPT_DIR/sample_tasks.sql"
    
    if [ $? -eq 0 ]; then
        echo "✅ 数据库记录已导入"
    else
        echo "❌ 数据库记录导入失败"
        exit 1
    fi
else
    echo "❌ 未找到数据库备份文件"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              ✅ 示例数据恢复完成！                    ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  提示：                                               ║"
echo "║  - 已恢复 5 张示例图片                                ║"
echo "║  - 刷新浏览器页面即可看到                             ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
RESTORE_SCRIPT

chmod +x "$BACKUP_DIR/restore.sh"
echo "✅ 恢复脚本已创建: $BACKUP_DIR/restore.sh"

# 4. 创建README
cat > "$BACKUP_DIR/README.md" << 'README'
# QwenImg 示例数据

这个目录包含了 QwenImg 的示例数据，用于在新环境中快速展示应用效果。

## 内容

- `outputs/` - 5 张示例图片
- `sample_tasks.sql` - 数据库记录
- `restore.sh` - 一键恢复脚本

## 使用方法

在新环境中恢复示例数据：

```bash
cd demo_data_backup
./restore.sh
```

## 注意事项

- 请确保已完成 `./install.sh` 安装
- 恢复脚本会自动复制图片和导入数据库记录
- 不会覆盖已有数据，只会添加新记录
README

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              ✅ 备份完成！                            ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  备份位置: $BACKUP_DIR/                               ║"
echo "║                                                       ║"
echo "║  包含内容：                                           ║"
echo "║  - $COPIED_COUNT 张示例图片                                      ║"
echo "║  - 数据库记录                                         ║"
echo "║  - 恢复脚本                                           ║"
echo "║                                                       ║"
echo "║  在新环境中恢复：                                     ║"
echo "║  cd $BACKUP_DIR && ./restore.sh                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
