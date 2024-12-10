Program:
  instructions*=Instruction
;

Instruction:
  Definition | Declaration | Execution | Comment
;

Definition:
  'define' name=ID '(' inputs=INT ':' outputs=INT ')' '{'
  inclusions+=Inclusion
  connections+=Connection
  '}'
;

Inclusion:
  'include' gate=ID ':' identifier=ID
;

Declaration:
  'declare' gate=ID ':' identifier=ID
;

Node:
  (instance='this' | instance=ID) '.' (side='in' | side='out') '[' index=INT ']'
;

Connection:
  source=Node '->' target=Node
;

Execution:
  circuit=ID '[' values+=INT[','] ']' 
;

Comment:
  /\/\/.*$/
;
