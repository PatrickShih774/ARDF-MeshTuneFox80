# =============================================================================
# ARDF-MeshTuneFox80 —— 双仓分离纪律校验
#
# 🔴 铁律：
#     硬件 / 文档 / 验证 / 许可  →  公开仓 ARDF-MeshTuneFox80
#     固件源码 / 构建文件 / 工具  →  私有仓 ARDF-MeshTuneFox80-firmware
#
# 本脚本扫描两个仓库的**已入库文件**（git ls-files，不看工作区），
# 发现越界即报错退出（退出码 1），可用于本地自检与 CI 门禁。
#
# 用法：
#   pwsh -File scripts/check-repo-separation.ps1
#   pwsh -File scripts/check-repo-separation.ps1 -PublicRepo <路径> -PrivateRepo <路径>
#
# 背景：见 docs/adr/ADR-0007-firmware-closed-source-two-repo.md 与
#       docs/08-licensing-and-compliance.md
# =============================================================================

[CmdletBinding()]
param(
    # 默认按「容器布局」推断：本脚本位于 <容器>/ARDF-MeshTuneFox80-hardware/scripts/
    [string]$PublicRepo  = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$PrivateRepo = (Join-Path (Split-Path (Resolve-Path (Join-Path $PSScriptRoot '..')).Path -Parent) 'ARDF-MeshTuneFox80-firmware')
)

$ErrorActionPreference = 'Stop'
$violations = New-Object System.Collections.Generic.List[string]

function Get-TrackedFiles {
    param([string]$Repo)
    if (-not (Test-Path (Join-Path $Repo '.git'))) {
        throw "不是 git 仓库（缺 .git）：$Repo"
    }
    return @(git -C $Repo ls-files)
}

Write-Host "=== 双仓分离纪律校验 ===" -ForegroundColor Cyan
Write-Host ("  公开仓: " + $PublicRepo)
Write-Host ("  私有仓: " + $PrivateRepo)
Write-Host ""

# -----------------------------------------------------------------------------
# 一、公开仓【禁止】出现固件源码与构建文件
# -----------------------------------------------------------------------------
$pubPatterns = [ordered]@{
    'C/C++ 源文件'        = '\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$'
    '汇编源文件'          = '\.(s|S|asm)$'
    'ESP-IDF 构建脚本'    = '(^|/)CMakeLists\.txt$'
    'sdkconfig 系列'      = '(^|/)sdkconfig(\.|$)'
    '分区表'              = '(^|/)partitions\.csv$'
    'Kconfig 系列'        = '(^|/)Kconfig(\.[a-z]+)?$'
    '版本文件'            = '(^|/)version\.txt$'
    '固件产物'            = '\.(bin|elf|map|hex)$'
}

$pubFiles = Get-TrackedFiles $PublicRepo
foreach ($rule in $pubPatterns.GetEnumerator()) {
    $hit = @($pubFiles | Where-Object { $_ -match $rule.Value })
    if ($hit.Count -gt 0) {
        foreach ($f in $hit) { $violations.Add("公开仓出现【$($rule.Key)】: $f") }
    }
}

# 公开仓允许保留的例外（明确白名单，避免误伤）
$pubAllowList = @(
    'software/README.md'        # 双仓结构说明（方案 B 占位）
    'NOTICE'                    # 第三方声明
)
$violations = New-Object System.Collections.Generic.List[string]($violations | Where-Object {
    $v = $_
    -not ($pubAllowList | Where-Object { $v -match [regex]::Escape($_) })
})

# -----------------------------------------------------------------------------
# 二、私有仓【禁止】出现硬件设计文件
# -----------------------------------------------------------------------------
$privPatterns = [ordered]@{
    'KiCad 工程'    = '\.(kicad_pcb|kicad_sch|kicad_pro|kicad_prl)$'
    'EDA 源文件'    = '\.(sch|brd|lay6|epro)$'
    'Gerber / 钻孔' = '\.(gbr|gtl|gbl|gts|gbs|gto|gbo|gko|drl|nc)$'
    '机械 / 3D'     = '\.(step|stp|stl|dxf|dwg)$'
    '数据手册'      = '\.pdf$'
    'BOM / 成本表'  = '(^|/)(bom|BOM)[^/]*\.(csv|xlsx|xls)$'
}

$privFiles = Get-TrackedFiles $PrivateRepo
foreach ($rule in $privPatterns.GetEnumerator()) {
    $hit = @($privFiles | Where-Object { $_ -match $rule.Value })
    if ($hit.Count -gt 0) {
        foreach ($f in $hit) { $violations.Add("私有仓出现【$($rule.Key)】: $f") }
    }
}

# -----------------------------------------------------------------------------
# 三、公开仓的 software/ 只允许 README（防止误把中控软件/固件放进公开仓）
# -----------------------------------------------------------------------------
$soft = @($pubFiles | Where-Object { $_ -match '^software/' })
foreach ($f in $soft) {
    if ($f -ne 'software/README.md') {
        $violations.Add("公开仓 software/ 只允许 README.md（双仓结构说明），出现: $f")
    }
}

# -----------------------------------------------------------------------------
# 结果
# -----------------------------------------------------------------------------
Write-Host ("  公开仓已入库文件: " + $pubFiles.Count)
Write-Host ("  私有仓已入库文件: " + $privFiles.Count)
Write-Host ""

if ($violations.Count -eq 0) {
    Write-Host "✅ 通过：双仓分离纪律未被破坏。" -ForegroundColor Green
    Write-Host ""
    Write-Host "  硬件 / 文档 / 验证 / 许可 -> 公开仓" -ForegroundColor DarkGray
    Write-Host "  固件源码 / 构建文件 / 工具 -> 私有仓" -ForegroundColor DarkGray
    exit 0
}

Write-Host ("🔴 发现 " + $violations.Count + " 处越界：") -ForegroundColor Red
foreach ($v in $violations) { Write-Host ("  ✗ " + $v) -ForegroundColor Red }
Write-Host ""
Write-Host "处置：把这些文件移入正确的仓库后重新提交。" -ForegroundColor Yellow
Write-Host "  固件源码/构建文件 -> 私有仓 ARDF-MeshTuneFox80-firmware" -ForegroundColor Yellow
Write-Host "  硬件设计文件      -> 公开仓 ARDF-MeshTuneFox80" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ 若已推送到公开仓，仅仅 git rm 不够：历史里仍有该文件。" -ForegroundColor Yellow
Write-Host "   必须删除并重建公开仓（见 docs/08-licensing-and-compliance.md §6）。" -ForegroundColor Yellow
exit 1
