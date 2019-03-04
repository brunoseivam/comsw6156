typedef void caEventCallbackFunc(int arg);

int main(void) {
    caEventCallbackFunc *cb = NULL;
    cb(0);
    return 0;
}