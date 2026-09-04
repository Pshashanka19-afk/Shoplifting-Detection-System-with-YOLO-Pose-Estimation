Write-Host "Setting up Shoplifting Detection System..."

Write-Host "Installing dependencies..."
pip install -r ..\requirements.txt

Write-Host "Starting FastAPI Backend..."
cd ..\backend
uvicorn app:app  --reload
