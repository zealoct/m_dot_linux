**tmux** must be compiled with /opt/compiler/gcc-4.8.2, jumbo gcc will not work,
otherwise there will be problem that cannot find `forkpty()` in libutil.

install **automake-1.15** before **global-6.5**.

all installation could be done using

    ./configure --prefix=$HOME/usr
    make && make install