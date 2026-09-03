#!/bin/sh

# Install prequisites
sudo apt update
sudo apt install -y mingw-w64 osslsigncode libz-mingw-w64-dev fpc libicu-dev 

# Install go
wget https://go.dev/dl/go1.27.1.linux-amd64.tar.gz -O /tmp/go1.27.1.linux-amd64.tar.gz
rm -rf /usr/local/go && sudo tar -C /usr/local -xzf /tmp/go1.27.1.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.zshrc
source ~/.zshrc

# Install dotnet
curl -L https://dot.net/v1/dotnet-install.sh | bash

# Install rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup target add x86_64-pc-windows-gnu

# Install nim
curl https://nim-lang.org/choosenim/init.sh -sSf | sh
echo 'export PATH=/home/kali/.nimble/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
nimble install winim nimcrypto zippy uuid4 puppy

# Install fpc
export FPCVER="3.2.2"
wget https://sourceforge.net/projects/freepascal/files/Source/$FPCVER/fpc-$FPCVER.source.zip/download -O /tmp/fpc-$FPCVER.source.zip
unzip /tmp/$FPCVER.source.zip -d /tmp
cd /tmp/$FPCVER/
sudo make crossinstall OS_TARGET=win64 CPU_TARGET=x86_64 INSTALL_PREFIX=/usr/
sudo fpcmkcfg -p -d "basepath=/usr/lib/fpc/$FPCVER" -o /etc/fpc.cfg
