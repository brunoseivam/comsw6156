#[derive(Debug)]
struct Dummy(i32);

fn main() {
    let a = Dummy(42);
    drop(a);
    println!("{:?}", a);
}