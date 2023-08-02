@echo off
echo Clearing up previous layer build...
del /s /q lambda-layer > nul 2>&1
rmdir /s /q lambda-layer > nul 2>&1
del /q lambda-layer.zip > nul 2>&1

echo Installing required packages...
C:\Windows\py.exe -m pip install --target lambda-layer/python/lib/python3.11/site-packages -r requirements.txt > nul 2>&1

echo Building layer...
pushd lambda-layer
C:\Windows\System32\tar.exe acf ..\lambda-layer.zip python > nul 2>&1
popd

echo All done. Now upload lambda-layer.zip to AWS Lambda.
