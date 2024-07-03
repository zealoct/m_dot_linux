#!/bin/bash

dir=$(cd $(dirname $BASH_SOURCE[0]) && pwd)

# Copy conf files

rm -f $HOME/.bash_profile && ln -s $dir/bash/bash_profile $HOME/.bash_profile
rm -f $HOME/.bashrc && ln -s $dir/bash/bashrc $HOME/.bashrc
rm -f $HOME/.bash_common && ln -s $dir/bash/bash_common $HOME/.bash_common
rm -f $HOME/.zshrc && ln -s $dir/zsh/zshrc $HOME/.zshrc
rm -f $HOME/.tmux.conf && ln -s $dir/tmux/tmux.conf $HOME/.tmux.conf
rm -f $HOME/.gitconfig && ln -s $dir/git/gitconfig $HOME/.gitconfig

mkdir -p $HOME/.mzsh && cp -r $dir/zsh/zsh-git-prompt $HOME/.mzsh/

# Binaries
mkdir -p $HOME/usr
ln -s $dir/bin $HOME/usr

# vim files
rm -rf $HOME/.vim
ln -s $dir/dot_vim $HOME/.vim
ln -s $HOME/.vim/vimrc $HOME/.vimrc

# emacs
ln -s $dir/emacs $HOME/.emacs.d

# Install jumbo
bash -c "$( curl http://jumbo.baidu.com/install_jumbo.sh )"

source ~/.bash_profile
