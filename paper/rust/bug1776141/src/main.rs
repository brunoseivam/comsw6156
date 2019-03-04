struct MsgBuff {
    message: [u8; 128]
}

fn main() {
    let mut m = MsgBuff {
        message: [0; 128]
    };

    let type_ = "dummy";
    let pdbentry = "dummy";
    let pfield_name =
        "123456789012345678901234567890\
         123456789012345678901234567890\
         123456789012345678901234567890\
         123456789012345678901234567890\
         123456789012345678901234567890";

    let formatted = format!("{:<4}L {} {}",
        pfield_name, type_, pdbentry);
    m.message.copy_from_slice(formatted.as_bytes());
}
