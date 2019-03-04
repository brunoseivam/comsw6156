use std::thread;

fn main() {
    let mut counter = 0;
    let mut handles = vec![]; 

    for _ in 0..10 {
        let handle = thread::spawn( || {
            counter += 1;
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Result: {}", counter);
}