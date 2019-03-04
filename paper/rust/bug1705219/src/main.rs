fn get_str() -> &str {
    let s:&str = "dummy";
    return s;
}

fn main() {
    let s = get_str();
    println!("{}", s);
}
