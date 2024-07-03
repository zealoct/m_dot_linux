comake         :	Makefile自动生成工具
	能够帮你解决复杂的基础库编译依赖问题，建立规范的代码开发目录
version        : 	comake_1.0.1

命令行参数:
         -v            : 	显示当前的版本号信息
         -h            : 	显示详细的帮助文档
	 -C/--checkout	   : 	自动下载模块所需要的所有依赖，并编译, 注意如果库已经存在在本地，会将这个文件夹按日期备份，并重新checkout
    -b/--basepath=     : 	指定源代码所在文件，如果没有制定，表示为当前目录下的所有文件生成Makefile

建立一个工程文件
 -p/--project=[app, lib, sub]  : 建立一个工程文件必须的参数
	-p app	:	表示建立一个生成可执行文件的工程文件
	-p lib	:	表示建立一个生成静态链接库的工程文件
	-p so	:	表示建立一个生成动态链接库的工程文件
	-p sub	:	遍历指定目录下的makefile，生成调用这些Makefile的Makefile

         -o            : 	输出文件名

建立一个标准化开发环境(编写新模块的时候有用)
-s/--standard=[app, lib, so] [-o 文件夹名]	:	建立一个标准的工程目录
	如果不加-o 文件夹，表示在当前目录生成标准工程目录


例子:
	comake -p app [-o 制定工程文件名] 扫描当前的目录为它生成一个工程描述文件
	comake --checkout [制定工程文件名] 根据当前目录下的工程文件，生成Makefile
		ej:	comake --checkout comake.prj
		or:	comake comake.prj
		or:	comake #自动load当前文件夹名的.prj文件
	make

wiki : http://com.baidu.com/twiki/bin/view/Main/Comakedesign
mailto : com@baidu.com
