#include <thread>
#include <vector>


void incr(int* counter) {
    *counter += 1;
}

int main(void) {
    int counter = 0;
    std::vector<std::thread> handles;

    for (int i = 0; i < 10; ++i)
        handles.push_back(std::thread(incr, &counter));

    for (auto& handle : handles)
        handle.join();

    printf("Result: %d\n", counter);
}