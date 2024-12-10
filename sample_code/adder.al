define AND3(3:1){
    include AND:and0
    include AND:and1

    this.in[0] -> and0.in[0]
    this.in[1] -> and0.in[1]
    this.in[2] -> and1.in[0]
    and0.out[0] -> and1.in[1]
    and1.out[0] -> this.out[0]
}

declare AND3: test
test[0,0,1]
test[1,1,1]