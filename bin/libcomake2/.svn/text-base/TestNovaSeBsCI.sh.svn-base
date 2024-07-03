#!/bin/bash
COMAKE2=`pwd`/../comake2

make -C ..

rm -rf work-se-bs
mkdir -p work-se-bs
cd work-se-bs

export MAC=64
if [ $# == 1 ]
then
    echo "svn co -r $1 https://svn.baidu.com/app/ecom/nova/trunk/se app/ecom/nova/se"
    svn co -r $1 https://svn.baidu.com/app/ecom/nova/trunk/se app/ecom/nova/se
else
    echo "svn co https://svn.baidu.com/app/ecom/nova/trunk/se app/ecom/nova/se"
    svn co https://svn.baidu.com/app/ecom/nova/trunk/se app/ecom/nova/se
fi
cd app/ecom/nova/se/se-bs

$COMAKE2 -U -F
if [ $? != 0 ]
then
    exit 1
fi
$COMAKE2 -W -W -W
if [ $? != 0 ]
then
    exit 1
fi
$COMAKE2 -B -J 30 -F
if [ $? != 0 ]
then
    exit 1
fi
$COMAKE2
if [ $? != 0 ]
then
    exit 1
fi
make clean
make -j 30
if [ $? != 0 ]
then
    exit 1
fi

cd ../../../../../../
