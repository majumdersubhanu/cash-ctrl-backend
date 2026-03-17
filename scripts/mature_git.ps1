# mature_git.ps1 - Simulates a 1-month development history for CashCtrl

$ErrorActionPreference = "Stop"

# Configuration
$repoPath = "C:\Users\subhanu\PythonProjects\cash-ctrl-backend"
$tempRepo = Join-Path $env:TEMP "cash-ctrl-matured-$(Get-Random)"
$startDate = (Get-Date).AddDays(-30)
$author = "Subhanu Majumder <majumder.subhanu@gmail.com>"

Write-Host "Rebuilding history in $tempRepo..."

# Initialize temp repo
New-Item -ItemType Directory -Path $tempRepo -Force | Out-Null
Set-Location $tempRepo
git init | Out-Null
git config user.name "Subhanu Majumder"
git config user.email "majumder.subhanu@gmail.com"

# Helper to commit with date
function Commit-Matured ($msg, $daysOffset, $hoursOffset) {
    $commitDate = $startDate.AddDays($daysOffset).AddHours($hoursOffset).ToString("yyyy-MM-ddTHH:mm:ss")
    $env:GIT_AUTHOR_DATE = $commitDate
    $env:GIT_COMMITTER_DATE = $commitDate
    git add .
    git commit -m $msg --quiet
}

# --- WEEK 1: ARCHITECTURE & IDENTITY ---
Write-Host "Processing Week 1..."
# Commit 1: Project Skeleton
$srcFiles = Get-ChildItem -Path $repoPath -Exclude ".git", ".github", "node_modules", ".venv", "__pycache__"
# Initially just add core files (manage.py, app/, requirements)
Copy-Item (Join-Path $repoPath "manage.py") $tempRepo
Copy-Item (Join-Path $repoPath "requirements.txt") $tempRepo
Copy-Item (Join-Path $repoPath "app") $tempRepo -Recurse
Commit-Matured "chore: initialize project architecture with django 6.x" 0 10

# Commit 2: User Model & Auth
Copy-Item (Join-Path $repoPath "users") $tempRepo -Recurse
Commit-Matured "feat(users): implement custom user model and base authentication" 2 14

# Commit 3: Accounts Module
Copy-Item (Join-Path $repoPath "accounts") $tempRepo -Recurse
Commit-Matured "feat(accounts): implement polymorphic accounts and currency engine" 4 11

# --- WEEK 2: THE LEDGER CORE ---
Write-Host "Processing Week 2..."
# Commit 4: Transactions & Categories
git checkout -b feature/core-ledger | Out-Null
Copy-Item (Join-Path $repoPath "transactions") $tempRepo -Recurse
Commit-Matured "feat(transactions): core ledger implementation with atomic updates" 7 15
git checkout master | Out-Null
git merge feature/core-ledger --no-ff -m "merge: core ledger feature branch" | Out-Null

# Commit 5: Split Engine v1
Copy-Item (Join-Path $repoPath "splits") $tempRepo -Recurse
Commit-Matured "feat(splits): mathematical engine for group expense splitting" 10 9

# --- WEEK 3: ADVANCED FINTECH ---
Write-Host "Processing Week 3..."
# Commit 6: P2P Lending
git checkout -b feature/lending-engine | Out-Null
Copy-Item (Join-Path $repoPath "lending") $tempRepo -Recurse
Commit-Matured "feat(lending): end-to-end p2p lending and amortization" 14 16
git checkout master | Out-Null
git merge feature/lending-engine --no-ff -m "merge: p2p lending engine" | Out-Null

# Commit 7: Analytics & Services
Copy-Item (Join-Path $repoPath "analytics") $tempRepo -Recurse
Commit-Matured "feat(analytics): spending forecasts and cashflow projections" 17 12

# Commit 8: Vision/OCR
Copy-Item (Join-Path $repoPath "integrations") $tempRepo -Recurse
Commit-Matured "feat(integrations): third-party stubs and ocr vision hooks" 20 18

# --- WEEK 4: ECOSYSTEM & OPS ---
Write-Host "Processing Week 4..."
# Commit 9: Monitoring Stack
git checkout -b feature/observability | Out-Null
Copy-Item (Join-Path $repoPath "docker-compose.yml") $tempRepo
Copy-Item (Join-Path $repoPath "Dockerfile") $tempRepo
Copy-Item (Join-Path $repoPath "prometheus") $tempRepo -Recurse -ErrorAction SilentlyContinue
Copy-Item (Join-Path $repoPath "grafana") $tempRepo -Recurse -ErrorAction SilentlyContinue
Commit-Matured "feat(ops): containerize stack with full observability (prometheus/grafana)" 24 10
git checkout master | Out-Null
git merge feature/observability --no-ff -m "merge: observability stack" | Out-Null

# Commit 10: Phone & Google Auth
Copy-Item (Join-Path $repoPath "GCLOUD_DEPLOYMENT.md") $tempRepo
Commit-Matured "docs(deploy): add comprehensive google cloud deployment guide" 27 15

# Commit 11: Documentation & Polish (Final State)
# Copy everything remaining
Copy-Item (Join-Path $repoPath "*") $tempRepo -Recurse -Force
Commit-Matured "docs: polish api specs and finalize enterprise documentation" 30 14

Write-Host "History rebuilt successfully. Ready to swap .git directories."
