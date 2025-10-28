# FireBird_dumper
The scripts were created because I couldn't find anything working properly


# install linux/macos
```
git clone https://github.com/PanAdamski/FireBird_dumper; cd FireBird_dumper
sudo apt update && sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install firebirdsql
```

# Install windows
```
git clone https://github.com/PanAdamski/FireBird_dumper; cd FireBird_dumper
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install firebirdsql
```

# Run
```
python3 autodump.py 192.168.100.100
```
```
python3 firebird_bruteforce.py -i 192.168.100.100 -u usernames.txt -p passwords.txt
```
