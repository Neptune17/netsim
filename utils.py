def strip_to_intip(strip):
    ips = strip.split(".")
    return (int(ips[0]) << 24) + (int(ips[1]) << 16) + (int(ips[2]) << 8) + (int(ips[3]) << 0)

def intip_to_strip(intip):
    a = (intip >> 24) & 0xff
    b = (intip >> 16) & 0xff
    c = (intip >> 8) & 0xff
    d = (intip >> 0) & 0xff
    return str(a) + "." + str(b) + "." + str(c) + "." + str(d)

def gen_subnet_mask(prefix_len):

    mask = 1
    for _ in range(prefix_len - 1):
        mask = mask << 1
        mask += 1
    for _ in range(32 - prefix_len):
        mask = mask << 1
    return mask

def strip_is_in_cidr(src_ip, cidr):
    cidr_prefix = cidr.split("/")[0]
    cidr_len = int(cidr.split("/")[1])

    # print(src_ip, cidr, (strip_to_intip(cidr_prefix) & gen_subnet_mask(cidr_len)) == (strip_to_intip(src_ip) & gen_subnet_mask(cidr_len)))

    return (strip_to_intip(cidr_prefix) & gen_subnet_mask(cidr_len)) == (strip_to_intip(src_ip) & gen_subnet_mask(cidr_len))