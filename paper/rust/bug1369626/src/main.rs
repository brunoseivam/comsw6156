type CaEventCallbackFunc = *const fn (i32) -> ();

fn main() {
    let cb : CaEventCallbackFunc = std::ptr::null();
    (*cb)(0);
}
