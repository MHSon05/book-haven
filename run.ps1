# ========================================================================
#  BookHaven E-Commerce System - PowerShell Launcher
#  Khởi chạy song song Backend FastAPI (:8000) và Frontend Vite (:5173)
# ========================================================================
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "                 HE THONG THUONG MAI DIEN TU BOOKHAVEN (v2.0)             " -ForegroundColor Green
Write-Host "   Tieu luan Phan tich & Thiet ke HTTT - B23DCAT262 - Hoc vien PTIT        " -ForegroundColor DarkGray
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Giai phong port 8000 va 5173 neu dang bi chiem
Write-Host "[*] Kiem tra va giai phong cong mang 8000 va 5173..." -ForegroundColor Yellow
$ports = @(8000, 5173)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pidToKill in $pids) {
            try {
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                Write-Host "    -> Da giai phong cong $p (PID: $pidToKill)" -ForegroundColor DarkYellow
            } catch {}
        }
    }
}

# 2. Xac dinh python
$pyExe = Join-Path $backendDir ".venv\Scripts\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = "python"
}

# 3. Kiem tra node_modules
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[*] Phat hien frontend chua co node_modules, dang cai dat..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
}

# 4. Khoi chay Backend FastAPI trong cua so rieng (chay thang uvicorn 1 tien trinh, tranh nap model AI 2 lan)
Write-Host "[1/2] Dang khoi dong Backend FastAPI (:8000)..." -ForegroundColor Cyan
$backendProc = Start-Process powershell.exe -PassThru -ArgumentList "-NoExit", "-Command", "Set-Location -LiteralPath '$backendDir'; & '$pyExe' -m uvicorn main:app --host 0.0.0.0 --port 8000"

# 5. Khoi chay Frontend Vite Dev trong cua so rieng
Write-Host "[2/2] Dang khoi dong Frontend Vite Dev (:5173)..." -ForegroundColor Cyan
$frontendProc = Start-Process powershell.exe -PassThru -ArgumentList "-NoExit", "-Command", "Set-Location -LiteralPath '$frontendDir'; npm run dev"

# 6. Cho ca Backend (:8000) va Frontend (:5173) san sang hoan toan roi moi mo trinh duyet
Write-Host "[*] Dang cho Backend (nap mo hinh AI) va Frontend san sang..." -ForegroundColor Yellow
$maxWaitSeconds = 120
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$backendReady = $false
$frontendReady = $false

while ($sw.Elapsed.TotalSeconds -lt $maxWaitSeconds) {
    if ($backendProc.HasExited) {
        Write-Host "[LOI] Cua so Backend da thoat som (ExitCode: $($backendProc.ExitCode)). Vui long kiem tra log." -ForegroundColor Red
        break
    }
    if ($frontendProc.HasExited) {
        Write-Host "[LOI] Cua so Frontend da thoat som (ExitCode: $($frontendProc.ExitCode)). Vui long kiem tra log." -ForegroundColor Red
        break
    }

    if (-not $backendReady) {
        try {
            $respBe = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($respBe.StatusCode -eq 200) {
                $backendReady = $true
                Write-Host ("    -> Backend (:8000) da san sang sau {0:N1}s" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Green
            }
        } catch {}
    }

    if (-not $frontendReady) {
        try {
            $respFe = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($respFe.StatusCode -eq 200) {
                $frontendReady = $true
                Write-Host ("    -> Frontend (:5173) da san sang sau {0:N1}s" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Green
            }
        } catch {}
    }

    if ($backendReady -and $frontendReady) {
        break
    }

    Start-Sleep -Milliseconds 500
}

if (-not ($backendReady -and $frontendReady)) {
    Write-Host ""
    Write-Host "[CANH BAO] Het thoi gian cho ($maxWaitSeconds giay) nhung may chu chua san sang day du:" -ForegroundColor Red
    Write-Host "  - Backend (:8000) : $backendReady" -ForegroundColor Red
    Write-Host "  - Frontend (:5173): $frontendReady" -ForegroundColor Red
    Write-Host "Trinh duyet se KHONG tu dong mo. Hay kiem tra 2 cua so dich vu." -ForegroundColor Yellow
    $opt = Read-Host "Nhan [Q] de tat tat ca may chu hoac Enter de thoat"
    if ($opt -eq "q" -or $opt -eq "Q") {
        foreach ($p in $ports) {
            $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
            if ($conns) {
                $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
                foreach ($pidToKill in $pids) {
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
    exit 1
}

Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "              HE THONG BOOKHAVEN DANG CHAY THANH CONG!                    " -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host "  Giao dien Nguoi Dung (Vite): http://localhost:5173" -ForegroundColor White
Write-Host "  Cong Backend REST API:        http://localhost:8000" -ForegroundColor White
Write-Host "  Tai lieu Swagger UI API:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "--------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  TAI KHOAN MAU:" -ForegroundColor Yellow
Write-Host "     - Admin   : admin / Mat khau: admin123 (Email: admin@bookhaven.vn)" -ForegroundColor White
Write-Host "     - User    : user / Mat khau: user123 (Email: user@bookhaven.vn)" -ForegroundColor White
Write-Host "==========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nhan [Q] de dung tat ca dich vu, hoac dong cac cua so rieng le." -ForegroundColor Yellow

$opt = Read-Host "Nhap [Q] de tat tat ca may chu"
if ($opt -eq "q" -or $opt -eq "Q") {
    Write-Host "[*] Dang dung tat ca cac dich vu va giai phong cong mang..." -ForegroundColor Yellow
    foreach ($p in $ports) {
        $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($pidToKill in $pids) {
                Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            }
        }
    }
    Write-Host "[OK] Da tat toan bo may chu!" -ForegroundColor Green
}
