NAME=$(shell basename "$(PWD)")

.PHONY: clean all

all: main-rust main-c main-cpp

# Rust
target/debug/$(NAME):
	cargo build

main-rust: target/debug/$(NAME)
	cp $< $@

# C
main-c: $(wildcard src/*.c)
	$(CC) -Wall -Wextra -o $@ $<

# C++
main-cpp: $(wildcard src/*.cpp)
	$(CXX) -Wall -Wextra -o $@ $<

clean:
	rm -f main-*
	cargo clean