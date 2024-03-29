CC=gcc
DEFINES=-DENDIAN_BIG=0 -DENDIAN_LITTLE=1
OS := $(shell uname -s)
ifeq ($(OS),Darwin)
   DEFINES+= -DHAVE_ACCEPT4=0
   # Avoid `fatal error: 'event.h' file not found` due to Homebrew
   # on Apple ARM installing libs to a non-default location.
   # https://github.com/orgs/Homebrew/discussions/868
   ifneq (,$(wildcard /opt/homebrew))
	   export CPATH=/opt/homebrew/include:${CPATH:-}
	   export LIBRARY_PATH=/opt/homebrew/lib:${LIBRARY_PATH:-}
	endif
else
   DEFINES+= -DHAVE_ACCEPT4=1
endif
CFLAGS+=-Wall -Werror $(DEFINES) $(CPPFLAGS)
OBJS=main.o client_data.o locks.o hash.o stats.o
LDFLAGS+=-levent -lm
HEADERS=prototypes.h client_data.h stats.h stats.list
DESTDIR ?=

poolcounterd: $(OBJS)
	$(CC) $^ $(LDFLAGS) -o $@

%.o: %.c $(HEADERS)
	$(CC) -c $(CFLAGS) $< -o $@

prototypes.h: main.c
	sed -n 's/\/\* prototype \*\//;/p' $^ > $@

clean:
	rm -f poolcounterd *.o prototypes.h

install:
	install -d $(DESTDIR)/usr/bin/
	install poolcounterd $(DESTDIR)/usr/bin/

# Depends on pytest and python3
test: poolcounterd
	pytest -v
