CFLAGS	= -DNDEBUG -march=native -Wno-char-subscripts -Wall -O3 -std=c++14 -I.
CXXFLAGS= ${CFLAGS}
LIBS = -lz -ltbb

.PHONY: all clean

all: count-collisions

count-collisions: count-collisions.o
	@echo "* Linking $@"
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS) $(LDFLAGS)

%.o: %.cpp
	@echo '* Compiling $<'
	$(CXX) $(CXXFLAGS) -o $@ -c $<

count-collisions.o: count-collisions.cpp kseq.h common.hpp argument_parser.hpp FastqSplitter.hpp kmer_utils.hpp xxhash.hpp

clean:
	rm -rf *.o count-collisions
