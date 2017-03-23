# UnichainDB

## Quick Start

### 1. Install [RethinkDB](https://rethinkdb.com/docs/install/ubuntu/) Server

Open a Terminal and run RethinkDB Server with the command
```
rethinkdb or rethinkdb --bind all
```
### 2. Env install and update
Ubuntu 14.04 already has Python 3.4, so you don\`t need to install it, but you do need to install others:

```
sudo apt-get update
sudo apt-get install g++ python3-dev
```
Get the latest version of pip and setuptools:
```
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip setuptools
```

### 3. Install the localdb
```
sudo apt-get install libleveldb1 libleveldb-dev libsnappy1 libsnappy-dev
sudo pip3 install plyvel

# localdb dir
sudo mkdir -p /data/localdb_unichain
sudo chown -R user[:group] /data/localdb_unichain
```

### 4. Start
```
unichain start
unichain_api start
```