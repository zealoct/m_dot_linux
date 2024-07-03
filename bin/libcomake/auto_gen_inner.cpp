
#ifdef __$MODULE_UPPER$___HAS_SHOW_VERSION
	extern char * __$MODULE_LOWER$___show_version();
	ret += snprintf(g_version_buf + ret, sizeof(g_version_buf) - ret,
			"%s\n", __$MODULE_LOWER$___show_version());
#else
	ret += snprintf(g_version_buf + ret, sizeof(g_version_buf) - ret,
			"%s\n", "__$LIB$__");
#endif
	if (ret >= (int)sizeof(g_version_buf)) {
		return g_version_buf;
	}

