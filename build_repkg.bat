@echo off
echo Build start
cd ./modules/repkg_src/RePKG
dotnet build RePKG.csproj -c Release /p:OutputType=Library
cd ./bin/Release
ren net472 repkg_dll
move /y repkg_dll ../repkg_dll
cd ..
move /y ./repkg_dll ../
cd ..
move /y ./repkg_dll ../
cd ..
move /y ./repkg_dll ../
echo Build ends.
echo Press any key to quit...
pause >nul