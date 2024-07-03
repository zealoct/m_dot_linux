#!/bin/bash

dir=$(dirname $0)

# Copy conf files
cp $dir/bash/bash_profile $HOME/.bash_profile
cp $dir/bash/bashrc $HOME/.bashrc
cp $dir/zsh/zshrc $HOME/.zshrc
cp $dir/tmux/tmux.conf $HOME/.tmux.conf

# Binaries
mkdir -p $HOME/usr
cp -r $dir/bin $home/usr/

# vim files
mkdir -p $HOME/.vim
cp -r $dir/dot_vim/* $HOME/.vim
ln -s $HOME/.vim/vimrc $HOME/.vimrc

# Install jumbo
bash -c "$( curl http://jumbo.baidu.com/install_jumbo.sh )"

source ~/.bash_profile
