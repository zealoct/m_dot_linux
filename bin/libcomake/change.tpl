HARDWARE_PLATFORM := $(shell uname -m)
ifeq ($(HARDWARE_PLATFORM),x86_64)
	release=__$outfile$__.64
else
	release=__$outfile$__.32
endif

all : target

target :
	make -f $(release)

debug :
	make debug -f $(release)

clean :
	make clean -f $(release)

output :
	make output -f $(release)

cov :
	make cov -f $(release)

ccpc :
	make ccpc -f $(release)

test :
	make test -f $(release)
