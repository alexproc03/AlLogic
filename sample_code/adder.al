define HALFADD(2:2) {
    include XOR: xor
    include AND: and

    // XOR gate for sum
    this.in[0] -> xor.in[0]
    this.in[1] -> xor.in[1]

    // AND gate for carry
    this.in[0] -> and.in[0]
    this.in[1] -> and.in[1]

    // XOR output is the sum
    xor.out[0] -> this.out[1]

    // AND output is the carry
    and.out[0] -> this.out[0]
}

define FULLADD(3:2) {
    include HALFADD: halfadd
    include HALFADD: halfadd1
    include OR: or

    this.in[0] -> halfadd1.in[1] //carryin
    this.in[1] -> halfadd.in[1] //b
    this.in[2] -> halfadd.in[0] //a

    halfadd.out[0] -> or.in[0]
    halfadd.out[1] -> halfadd1.in[0]

    halfadd1.out[0] -> or.in[1]
    or.out[0] -> this.out[0]
    halfadd1.out[1] -> this.out[1]
}

//bit 0: c in, input 1-8: first operand, input 9-16: second operand
//output: 0 carry out, litte endian
define EIGHTADD(17:9) {
    include FULLADD: bit0
    include FULLADD: bit1
    include FULLADD: bit2
    include FULLADD: bit3
    include FULLADD: bit4
    include FULLADD: bit5
    include FULLADD: bit6
    include FULLADD: bit7

    this.in[8] -> bit0.in[2]
    this.in[16] -> bit0.in[1]
    this.in[0] -> bit0.in[0]

    this.in[7] -> bit1.in[2]
    this.in[15] -> bit1.in[1]

    this.in[6] -> bit2.in[2]
    this.in[14] -> bit2.in[1]

    this.in[5] -> bit3.in[2]
    this.in[13] -> bit3.in[1]

    this.in[4] -> bit4.in[2]
    this.in[12] -> bit4.in[1]

    this.in[3] -> bit5.in[2]
    this.in[9] -> bit5.in[1]
    
    this.in[2] -> bit6.in[2]
    this.in[10] -> bit6.in[1]

    this.in[1] -> bit7.in[2]
    this.in[9] -> bit7.in[1]

    bit0.out[0] -> bit1.in[0]
    bit1.out[0] -> bit2.in[0]
    bit2.out[0] -> bit3.in[0]
    bit3.out[0] -> bit4.in[0]
    bit4.out[0] -> bit5.in[0]
    bit5.out[0] -> bit6.in[0]
    bit6.out[0] -> bit7.in[0]

    bit7.out[0] -> this.out[0]
    bit7.out[1] -> this.out[1]
    bit6.out[1] -> this.out[2]
    bit5.out[1] -> this.out[3]
    bit4.out[1] -> this.out[4]
    bit3.out[1] -> this.out[5]
    bit2.out[1] -> this.out[6]
    bit1.out[1] -> this.out[7]
    bit0.out[1] -> this.out[8]
}


declare EIGHTADD: test
test[0,            0,0,0,0,1,1,1,1,            0,0,0,0,1,0,0,0]

