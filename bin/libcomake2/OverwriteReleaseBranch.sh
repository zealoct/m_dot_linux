RB=https://svn.baidu.com/com/branches/tools/comake/com_1-0-85-1_BRANCH/
RB_NAME=com_1-0-85-1_BRANCH
DB=https://svn.baidu.com/com/branches/tools/comake/comake_development_BRANCH/
DB_NAME=comake_development_BRANCH

rm -rf .switch
mkdir .switch
cd .switch
svn co $RB
svn co $DB

cd $RB_NAME
find . -type f | grep -v "\.svn" | xargs rm -rf 
cd ..

cd $DB_NAME
find . -type f | grep "\.svn" | xargs rm -rf
cd ..

cp $DB_NAME/* -r $RB_NAME
cd $RB_NAME
cd libcomake2
svn add *
cd ..
svn ci -m "cherrypick"
cd ..

cd ..