#!/bin/sh

# Install prequisites
sudo apt update
sudo apt install -y mingw-w64 wine osslsigncode libz-mingw-w64-dev golang-go fpc libicu-dev nim

# Install dotnet
curl -L https://dot.net/v1/dotnet-install.sh | bassh

# Install rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup target add x86_64-pc-windows-gnu
rustup update stable
rustup target add x86_64-pc-windows-gnu

# Build fpc
wget https://sourceforge.net/projects/freepascal/files/Source/3.2.2/fpc-3.2.2.source.zip/download -O /tmp/fpc-3.2.2.source.zip
export FPCVER="3.2.2"
unzip /tmp/fpc-3.2.2.source.zip -d /tmp
cd /tmp/fpc-3.2.2/
sudo make crossinstall OS_TARGET=win64 CPU_TARGET=x86_64 INSTALL_PREFIX=/usr/
sudo fpcmkcfg -p -d "/usr/lib/fpc/3.2.2" -o /etc/fpc.cfg

# Install nim requirements
nimble install winim nimcrypto zippy uuid4