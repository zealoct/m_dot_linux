#----------------build target : __$NAME$__--------------------

__$NAME$__ : CC := __$CC_VALUE$__
__$NAME$__ : CXX := __$CXX_VALUE$__
__$NAME$__ : CXXFLAGS := __$CXXFLAGS_VALUE$__
__$NAME$__ : CPPFLAGS := __$CPPFLAGS_VALUE$__
__$NAME$__ : IDLFLAGS := __$IDLFLAGS_VALUE$__
__$NAME$__ : CFLAGS := __$CFLAGS_VALUE$__
__$NAME$__ : INCPATH := __$INCPATH_VALUE$__ $(DEP_INCPATH)
__$NAME$__ : LDLIBS := __$LDLIBS_VALUE$__ $(DEP_LDLIBS)
__$NAME$__ : LDFLAGS := __$LDFLAGS_VALUE$__ $(DEP_LDFLAGS)
__$NAME$__ : LINKFLAGS := __$LINKFLAGS_VALUE$__

__$FNAME$___SOURCES := $(wildcard __$SOURCES_VALUE$__)
#__$FNAME$___HEADERS := $(wildcard __$HEADERS_VALUE$__)
__$FNAME$___HEADERS := __$HEADERS_VALUE$__
__$FNAME$___IDLSRC := $(wildcard __$IDLSRC_VALUE$__)
__$FNAME$___IDLSRCCPP := $(patsubst %.idl,%.cpp, $(__$FNAME$___IDLSRC))
__$FNAME$___IDLSRCH := $(patsubst %.idl,%.h, $(__$FNAME$___IDLSRC))
__$FNAME$___CONFDES := $(wildcard __$CONFDES$_VALUE$__ __$NAME$__.des)
__$FNAME$___CONFRANGE := $(patsubst %.des,%.range, $(__$FNAME$___CONFDES))
__$FNAME$___OBJS := $(__$FNAME$___IDLSRC:.idl=.o)
__$FNAME$___OBJS += $(__$FNAME$___SOURCES:.c=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.cc=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.cpp=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.cxx=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.C=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.idl=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.yacc=.o)
__$FNAME$___OBJS := $(__$FNAME$___OBJS:.lex=.o)
__$NAME$__ : $(__$FNAME$___OBJS) __$DEPFILES_VALUE$__
__$LINKCMD_LINES$__

__$LIST_ALL_TARGET$__

#---------------------end build target : __$NAME$__------------------
