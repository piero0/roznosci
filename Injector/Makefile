DYNINST := /home/piero/projects/dyninst/bin
CXXFLAGS := -g -std=c++17 -I$(DYNINST)/include

all: target libcpp libc injector

target: target.o

libcpp: CXXFLAGS := -shared -fPIC -fvisibility=hidden -std=c++17
libcpp: LDLIBS := -lpthread
libcpp: libcpp.o
	$(CXX) $(CXXFLAGS) -o $@.so $^ $(LDLIBS)

libc: CFLAGS := -shared -fPIC
libc: libc.c
	$(CC) $(CFLAGS) -o $@.so $^

injector: LDLIBS := -ldyninstAPI -lstdc++
injector: LDFLAGS := -L$(DYNINST)/lib
injector: injector.o
