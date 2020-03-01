pip install tcod
wget https://github.com/Kaleado/disgaeablo/archive/master.zip -OutFile master.zip
rm .\disgaeablo-master
Expand-Archive -Path master.zip -DestinationPath ./
cp .\disgaeablo-master\update.ps1 .\update.ps1
rm master.zip
