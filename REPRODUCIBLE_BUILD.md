# REPRODUCIBLE BUILD INSTRUCTIONS (GAHENAX-GOLD)

## 1. Build Environment
- **OS**: Windows 10/11 x64
- **Python**: 3.13.5
- **Dependencies**: `pip install -r requirements.txt -r requirements-build.txt` (if exists, else just requirements.txt)

## 2. Verification Steps
Run these commands in order to certify a build:

```powershell
# 1. Clean previous artifacts
Remove-Item -Recurse -Force dist, build, __pycache__ -ErrorAction SilentlyContinue

# 2. Verify Code Integrity
python -m compileall app
if ($LASTEXITCODE -ne 0) { throw "Syntax Error" }

# 3. Functional Verification
python verify_mvp.py
python auditoria_semaforo.py

# 4. Security Scan
# (Manual check or script if available)
```

## 3. Packaging (Portable)
```powershell
python build_portable.py
```
Expected Output: `./dist/ChechyLegis_Portable.zip`
SHA256 Signature must be recorded.

## 4. Docker Build
```bash
docker build -t chechylegis:gold .
docker run --rm -p 8000:8000 chechylegis:gold
curl http://localhost:8000/api/health
```

## 5. Artifact Hashing
All final artifacts must be hashed:
```powershell
Get-FileHash ./dist/ChechyLegis_Portable.zip -Algorithm SHA256 > SHA256SUMS.txt
```
