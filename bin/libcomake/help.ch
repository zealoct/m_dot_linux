comake         :	Makefile�Զ����ɹ���
	�ܹ����������ӵĻ���������������⣬�����淶�Ĵ��뿪��Ŀ¼
version        : 	comake_1.0.1

�����в���:
         -v            : 	��ʾ��ǰ�İ汾����Ϣ
         -h            : 	��ʾ��ϸ�İ����ĵ�
	 -C/--checkout	   : 	�Զ�����ģ������Ҫ������������������, ע��������Ѿ������ڱ��أ��Ὣ����ļ��а����ڱ��ݣ�������checkout
    -b/--basepath=     : 	ָ��Դ���������ļ������û���ƶ�����ʾΪ��ǰĿ¼�µ������ļ�����Makefile

����һ�������ļ�
 -p/--project=[app, lib, sub]  : ����һ�������ļ�����Ĳ���
	-p app	:	��ʾ����һ�����ɿ�ִ���ļ��Ĺ����ļ�
	-p lib	:	��ʾ����һ�����ɾ�̬���ӿ�Ĺ����ļ�
	-p so	:	��ʾ����һ�����ɶ�̬���ӿ�Ĺ����ļ�
	-p sub	:	����ָ��Ŀ¼�µ�makefile�����ɵ�����ЩMakefile��Makefile

         -o            : 	����ļ���

����һ����׼����������(��д��ģ���ʱ������)
-s/--standard=[app, lib, so] [-o �ļ�����]	:	����һ����׼�Ĺ���Ŀ¼
	�������-o �ļ��У���ʾ�ڵ�ǰĿ¼���ɱ�׼����Ŀ¼


����:
	comake -p app [-o �ƶ������ļ���] ɨ�赱ǰ��Ŀ¼Ϊ������һ�����������ļ�
	comake --checkout [�ƶ������ļ���] ���ݵ�ǰĿ¼�µĹ����ļ�������Makefile
		ej:	comake --checkout comake.prj
		or:	comake comake.prj
		or:	comake #�Զ�load��ǰ�ļ�������.prj�ļ�
	make

wiki : http://com.baidu.com/twiki/bin/view/Main/Comakedesign
mailto : com@baidu.com
