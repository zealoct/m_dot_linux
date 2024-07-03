#!/bin/bash
COMAKE2=`pwd`/../comake2

function call_comake(){
    $COMAKE2 -C work -F -U 1>/dev/null 2>error.log
    if [ $? != 0 ]
    then
        cat error.log
        echo "failed"
        exit -1
    fi
    export MAC=64
    $COMAKE2 -C work -F -B 1>/dev/null 2>error.log
    if [ $? != 0 ]
    then
        cat error.log
        echo "failed"
        exit -1
    fi
    $COMAKE2 -C work 1>/dev/null 2>error.log
    if [ $? != 0 ]
    then
        cat error.log
        echo "failed"
        exit -1
    fi
}

function check_exit(){
    if [ $? != 0 ]
    then
        echo "failed"
        exit -1
    fi
}

function setup(){
    rm -rf tmp
    mkdir -p tmp
    cd tmp
}

function teardown(){
    cd ../
    rm -rf tmp
}

function case_1(){
    echo -n "case1:"
    setup
    
    $COMAKE2 -E public/ub 2>&1 1>/dev/null
    check_exit    
    $COMAKE2 -E public/ub@1.0.0.0 2>&1 1>/dev/null
    check_exit
    
    teardown
    echo "succeed"
}

function case_2(){
    echo -n "case2:"
    setup

    echo "#include \"ddd\"
int main(){}" > test.cpp
    echo "WORKROOT('.')
Application('test',Sources('test.cpp'))" > COMAKE    
    $COMAKE2 1>/dev/null 2>err
    content=`grep "Fatal" err`
    if [ -z "$content" ] 
    then
        echo "failed"
        exit -1
    fi
    
    teardown
    echo "succeed"
}

function case_3(){
    echo -n "case3:"    
    setup
    
    mkdir -p work/include
    echo "#include \"./include/y.idl\"
#include \"./z.idl\"
struct x{y a;z b;};" > work/x.idl
    echo "struct y{int8_t a;};" > work/include/y.idl
    echo "struct z{int8_t a;};" > work/include/z.idl
    echo "WORKROOT('../')
CONFIGS('public/idlcompiler')
IDLFLAGS('-I ./include --compack')
UBRPCFLAGS('-I ./include --comapck')
StaticLibrary('work',Sources('x.idl'))" > work/COMAKE    
    call_comake
    content=`grep "include/v.idl" work/Makefile`
    if [ -n "$content" ]
    then
        echo "failed"
        return -1
    fi    
    make -C work -j 30 2>&1 1>/dev/null
    check_exit
    
    teardown
    echo "succeed"
}

function case_4(){
    echo -n "case4:"
    setup

    mkdir -p work/src
    echo "#include <cstdio>
int main(){printf(\"%s\n\",VERSION);}" > work/src/x.cpp
    echo "WORKROOT('../')
CPPFLAGS('-DVERSION=\"\\\\\"%s\\\\\"\"'%(BuildVersion()))
Application('./src/x',Sources('./src/x.cpp'))" > work/COMAKE    
    COMAKE2_BUILD_VERSION=1.0.0.0 call_comake
    make -C work -j 30 2>&1 1>/dev/null
    check_exit
    content=`./work/output/bin/x`
    if [ $content != "1.0.0.0" ]
    then
        echo "failed"
        exit -1
    fi
    
    teardown
    echo "succeed"
}

function case_5(){
    echo -n "case5:"
    setup
    
    mkdir -p work/src
    echo "int echo(const char *s){}" > work/src/echo.cpp
    echo "extern int echo(const char *s);" > work/src/echo.h
    echo "#include \"echo.h\"
int main(){}" > work/main.cpp
    echo "int main(){}" > work/main2.cpp
    echo "WORKROOT('.')
INCPATHS('$/src/')
LIBS('src/libecho.a')
StaticLibrary('src/echo',Sources('src/echo.cpp'))
Application('main',Libraries('src/libecho.a')+ENV.Libraries(),
Sources('test.cpp main.cpp')-Sources('test.cpp'))
Application('main2',ENV.Libraries(),
Sources('test.cpp main2.cpp')-Sources('test.cpp'))" > work/COMAKE    
    call_comake
    make -C work -j 30 2>&1 1>/dev/null
    check_exit
    teardown
    echo "succeed"
}

case_1
case_2
case_3
case_4
case_5