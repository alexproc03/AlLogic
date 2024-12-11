define OR8(8:1) {
    include OR: or1
    include OR: or2
    include OR: or3
    include OR: or4
    include OR: or5
    include OR: or6
    include OR: or7

    this.in[0] -> or1.in[0]
    this.in[1] -> or1.in[1]

    this.in[2] -> or2.in[0]
    this.in[3] -> or2.in[1]

    this.in[4] -> or3.in[0]
    this.in[5] -> or3.in[1]

    this.in[6] -> or4.in[0]
    this.in[7] -> or4.in[1]

    or1.out[0] -> or5.in[0]
    or2.out[0] -> or5.in[1]

    or3.out[0] -> or6.in[0]
    or4.out[0] -> or6.in[1]

    or5.out[0] -> or7.in[0]
    or6.out[0] -> or7.in[1]

    or7.out[0] -> this.out[0]
}

define AND4(4:1) {
    include AND: and1
    include AND: and2
    include AND: and3

    this.in[0] -> and1.in[0]
    this.in[1] -> and1.in[1]

    this.in[2] -> and2.in[0]
    this.in[3] -> and2.in[1]

    and1.out[0] -> and3.in[0]
    and2.out[0] -> and3.in[1]

    and3.out[0] -> this.out[0]
}

//inputs: 0-7, lines: 8-10 little endian
define MUX8(11: 1) {
    include NOT: not0
    include NOT: not1
    include NOT: not2

    include AND4: line0
    include AND4: line1
    include AND4: line2
    include AND4: line3
    include AND4: line4
    include AND4: line5
    include AND4: line6
    include AND4: line7

    include OR8: accumulator

    this.in[0] -> line0.in[0]
    this.in[1] -> line1.in[0]
    this.in[2] -> line2.in[0]
    this.in[3] -> line3.in[0]
    this.in[4] -> line4.in[0]
    this.in[5] -> line5.in[0]
    this.in[6] -> line6.in[0]
    this.in[7] -> line7.in[0]

    //not gates
    this.in[10] -> not0.in[0]
    this.in[9] -> not1.in[0]
    this.in[8] -> not2.in[0]

    //0: this.in[10]
    //1: this.in[9]
    //2: this.in[8]

    //line0: !0, !1, !2
    not0.out[0] -> line0.in[1]
    not1.out[0] -> line0.in[2]
    not2.out[0] -> line0.in[3]

    //line1: 0, !1, !2
    this.in[10] -> line1.in[1]
    not1.out[0] -> line1.in[2]
    not2.out[0] -> line1.in[3]

    //line2: !0, 1, !2
    not0.out[0] -> line2.in[1]
    this.in[9] -> line2.in[2]
    not2.out[0] -> line2.in[3]

    //line3: 0, 1, !2
    this.in[10] -> line3.in[1]
    this.in[9] -> line3.in[2]
    not2.out[0] -> line3.in[3]

    //line4: !0, !1, 2
    not0.out[0] -> line4.in[1]
    not1.out[0] -> line4.in[2]
    this.in[8] -> line4.in[3]

    //line5: 0, !1, 2
    this.in[10] -> line5.in[1]
    not1.out[0] -> line5.in[2]
    this.in[8] -> line5.in[3]

    //line6: !0, 1, 2
    not0.out[0] -> line6.in[1]
    this.in[9] -> line6.in[2]
    this.in[8] -> line6.in[3]

    //line7: 0, 1, 2
    this.in[10] -> line7.in[1]
    this.in[9] -> line7.in[2]
    this.in[8] -> line7.in[3]

    line0.out[0] -> accumulator.in[0]
    line1.out[0] -> accumulator.in[1]
    line2.out[0] -> accumulator.in[2]
    line3.out[0] -> accumulator.in[3]
    line4.out[0] -> accumulator.in[4]
    line5.out[0] -> accumulator.in[5]
    line6.out[0] -> accumulator.in[6]
    line7.out[0] -> accumulator.in[7]

    accumulator.out[0] -> this.out[0]
}

declare MUX8: test
test[1,1,0,1,1,1,1,1, 0,1,0]
