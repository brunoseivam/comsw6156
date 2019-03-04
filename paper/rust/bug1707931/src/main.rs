fn main() {
    let u = 42u32;
    if u < 0 {
        println!("Should never happen");
    }

    let i = -42i32;
    let u:u32 = i;
    if u < 0 {
        println!("Should never happen");
    }
}
