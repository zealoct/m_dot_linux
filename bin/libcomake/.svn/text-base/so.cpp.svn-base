
#ifdef __cplusplus
extern "C" {
#endif

#define __$MODULE_NAME_UPCASE$___HAS_VERSION

static char g___$MODULE_NAME$___version[1024] = {0};

char * __$MODULE_NAME$___show_version() 
{
	return g___$MODULE_NAME$___version;
}

#ifndef LD_SO_PATH
#ifndef __i386
#define LD_SO_PATH "/lib64/ld-linux-x86-64.so.2"
#else
#define LD_SO_PATH "/lib/ld-linux.so.2"
#endif
#endif

const char interp[] __attribute__((section(".interp"))) = LD_SO_PATH;
void so_main()
{
	printf("loading %s...\n", interp);
	printf("%s\n", __$MODULE_NAME$___show_version();
	exit(0);
}

#ifdef __cplusplus
}
#endif


