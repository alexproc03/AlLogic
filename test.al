define halfAdder(2:2){
    include AND:and1
    include XOR:xor1

    this.in[0] -> and1.in[0]
    this.in[1] -> and1.in[1]
    this.in[0] -> xor1.in[0]
    this.in[1] -> xor1.in[1]
    and1.out[0] -> this.out[0]
    xor1.out[0] -> this.out[1]
}

declare halfAdder: test
test[1,1]