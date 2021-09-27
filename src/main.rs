use mandelrust::{rmandelbrot, rmandelbrot_mt};
use std::time::Instant;

const WIDTH: usize = 2000;
const HEIGHT: usize = 2000;
fn main() {
    let start = Instant::now();
    let _ = rmandelbrot(WIDTH, HEIGHT, -2.0, 1.0, -1.0, 1.0);
    println!("Single thread: {:?}", Instant::now() - start);

    let start = Instant::now();
    let _ = rmandelbrot_mt(WIDTH, HEIGHT, -2.0, 1.0, -1.0, 1.0);
    println!("Multiple threads: {:?}", Instant::now() - start);
}
