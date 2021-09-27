use num::Complex;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use rayon::prelude::*;

const MAX_ITER: usize = 100;

fn escape_time(c: Complex<f64>) -> usize {
    let mut z = Complex::new(0.0f64, 0.0);
    let mut n = 0;

    while z.norm() <= 2.0 && n < MAX_ITER {
        z = z * z + c;
        n += 1;
    }

    n
}

/// Generates a mandelbrot set image
pub fn rmandelbrot(
    width: usize,
    height: usize,
    left: f64,
    right: f64,
    top: f64,
    bottom: f64,
) -> Vec<u8> {
    let mut pixels = Vec::<u8>::with_capacity(width * height * 3);
    for y in 0..height {
        for x in 0..width {
            let c = Complex::new(
                left + (x as f64 / width as f64) * (right - left),
                bottom + (y as f64 / height as f64) * (top - bottom),
            );

            let color = (255 - escape_time(c) * 255 / MAX_ITER) as u8;
            pixels.push(color);
            pixels.push(color);
            pixels.push(color);
        }
    }
    pixels
}

/// Generates a mandelbrot set image using multiple threads
pub fn rmandelbrot_mt(
    width: usize,
    height: usize,
    left: f64,
    right: f64,
    top: f64,
    bottom: f64,
) -> Vec<u8> {
    let pixels: Vec<u8> = (0..height)
        .into_par_iter()
        .map(|y| {
            let row: Vec<u8> = (0..width)
                .map(move |x| {
                    let c = Complex::new(
                        left + (x as f64 / width as f64) * (right - left),
                        bottom + (y as f64 / height as f64) * (top - bottom),
                    );

                    let color = (255 - escape_time(c) * 255 / MAX_ITER) as u8;
                    [color, color, color]
                })
                .flatten()
                .collect();
            row
        })
        .flatten()
        .collect();
    pixels
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn mandelrust(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    /// Python function to call the Rust mandelbrot implementation
    pub fn mandelbrot(
        py: Python,
        width: usize,
        height: usize,
        left: f64,
        right: f64,
        top: f64,
        bottom: f64,
    ) -> PyObject {
        let pixels = rmandelbrot(width, height, left, right, top, bottom);
        PyBytes::new(py, &pixels).into()
    }

    #[pyfn(m)]
    pub fn mandelbrot_mt(
        py: Python,
        width: usize,
        height: usize,
        left: f64,
        right: f64,
        top: f64,
        bottom: f64,
    ) -> PyObject {
        let pixels = rmandelbrot_mt(width, height, left, right, top, bottom);
        PyBytes::new(py, &pixels).into()
    }

    Ok(())
}
