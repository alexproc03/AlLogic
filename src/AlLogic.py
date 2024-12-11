from collections import deque
import os
import random
import sys
from textx import metamodel_from_file

defined_gates = {}
declared_circuits = {}

class Gate:
    def __init__(self, identifier, num_inputs, num_outputs):
        self.identifier = identifier
        self.inputs = num_inputs
        self.outputs = num_outputs
        defined_gates.update({identifier:self})

class SimpleGate(Gate):
    def __init__(self, identifier, num_inputs, num_outputs, truth_table):
        super().__init__(identifier, num_inputs, num_outputs)
        self.truth_table = truth_table

class ComplexGate(Gate):
    def __init__(self, identifier, num_inputs, num_outputs):
        super().__init__(identifier, num_inputs, num_outputs)
        self.components = {}
        self.connections = []

    def add_component(self, gate, gate_identifier):
        self.components.update({gate_identifier: gate})

    def connect(self, from_gate:str, from_node: tuple, to_gate:str, to_node: tuple):
        self.connections.append((from_gate, from_node, to_gate, to_node))

class CircuitInstance:
    def __init__(self, name: str, gate: Gate):
        self.name = name
        self.type = gate
        self.input_nodes = [Node(self) for _ in range(gate.inputs)]  # New, unique input nodes
        self.output_nodes = [Node(self) for _ in range(gate.outputs)]  # New, unique output nodes
        self.sub_circuits = {}

        if isinstance(gate, ComplexGate):
            # Initialize sub-circuits recursively
            for identifier, sub_gate in gate.components.items():
                self.sub_circuits[identifier] = CircuitInstance(identifier, sub_gate)

            # Build graph based on connections specified in ComplexGate
            for from_gate, from_node, to_gate, to_node in gate.connections:
                circuit_from = self if from_gate == "this"  else self.sub_circuits.get(from_gate)
                circuit_to = self if to_gate == "this" else self.sub_circuits.get(to_gate)
                if from_node[0] == 'in':
                    node_object_from = circuit_from.input_nodes[from_node[1]]
                elif from_node[0] == 'out':
                    node_object_from = circuit_from.output_nodes[from_node[1]]
                else:
                    raise ValueError(f"{from_node[0]} is not \'in\' or \'out\'")
                if to_node[0] == 'in':
                    node_object_to = circuit_to.input_nodes[to_node[1]]
                elif to_node[0]  == 'out':
                    node_object_to = circuit_to.output_nodes[to_node[1]]
                else:
                    raise ValueError(f"{from_node[0]} is not \'in\' or \'out\'")
                node_object_to.set_source(node_object_from)
                node_object_from.dependents.append(node_object_to)

            for from_gate, from_node, to_gate, to_node in gate.connections:
                circuit_from = self if from_gate == "this"  else self.sub_circuits.get(from_gate)
                circuit_to = self if to_gate == "this" else self.sub_circuits.get(to_gate)
                node_object_from = circuit_from.input_nodes[from_node[1]] if from_node[0] == 'in' else circuit_from.output_nodes[from_node[1]]
        
        #evaluation of  to reach a valid initial state
        self.evaluate()

    def __str__(self):
        inputs = ', '.join(str(node.value) for node in self.input_nodes)
        outputs = ', '.join(str(node.value) for node in self.output_nodes)
        return f"Circuit '{self.name}' (Type: {self.type.identifier}): Inputs: [{inputs}] Outputs: [{outputs}]"

    def get_current_inputs(self):
        return [node.value for node in self.input_nodes]

    def get_current_outputs(self):
        return [node.value for node in self.output_nodes]

    def update_inputs(self, input_values):
        for node, value in zip(self.input_nodes, input_values):
            node.set_value(value)
        self.evaluate()

    def evaluate(self):
        if isinstance(self.type, SimpleGate):
            # Evaluate using truth table
            input_values = tuple(node.value for node in self.input_nodes)
            output_values = self.type.truth_table.get(input_values)
            for i in range(len(output_values)):
                self.output_nodes[i].value = output_values[i]
        elif isinstance(self.type, ComplexGate):
            # Propagation logic
            #instantiate a queue
            node_queue = deque([])
    
            #add input dependents to the queue
            for node in self.input_nodes:
                node.initialized = True
                node_queue.extendleft(node.dependents)
            while node_queue:
                current = node_queue.pop() # pop with lowest priority

                # save previous value for post-comparison
                previous_value = current.value

                #evaluate current node value
                #if a node has a source, update its value to the same as its source
                if current.source is not None:
                    current.value = current.source.value
                #otherwise, if node is an output of a SimpleGate, update its value based on node's owner's input values at that moment
                else:
                    upstream_inputs = tuple(node.value for node in current.owner.input_nodes) #grabs current inputs associated with the owner circuit
                    current_index = current.owner.output_nodes.index(current) #grabs index of current node in owner circuit
                    current.value = current.owner.type.truth_table.get(upstream_inputs)[current_index] #grabs specific output from all of them

                #queue dependents if circuit is being initialized or has been changed
                if not current.initialized or current.value != previous_value:
                    node_queue.extendleft(current.dependents)
                    #if a node is an input to a simplegate, add the simpleGate's outputs to the queue
                    if current in current.owner.input_nodes:
                        for dependent in current.owner.output_nodes:
                            node_queue.append(dependent)
                    current.initialized = True

# Node can have only 1 source, but multiple dependents
class Node:
    def __init__(self, gate: CircuitInstance):
        self.initialized = False
        self.value = 0
        self.source = None
        self.dependents = []
        self.owner = gate

    def set_value(self, value: int):
        self.value = value

    def set_source(self, source):
        self.source = source

    def __str__(self):
        return (f"Node(value={self.value}, has_source={self.source is not None}, "
                f"dependents={len(self.dependents)}, owner={self.owner})")

#define basic gates
nand_gate = SimpleGate('NAND', 2, 1, {(0, 0): (1,), (0, 1): (1,), (1, 0): (1,), (1, 1): (0,)})
not_gate = SimpleGate(identifier="NOT", num_inputs=1, num_outputs=1, truth_table={(0,): (1,), (1,): (0,)})
and_gate = SimpleGate(identifier="AND", num_inputs=2, num_outputs=1, truth_table={(0, 0): (0,), (0, 1): (0,), (1, 0): (0,), (1, 1): (1,)})
or_gate = SimpleGate(identifier="OR", num_inputs=2, num_outputs=1, truth_table={(0, 0): (0,), (0, 1): (1,), (1, 0): (1,), (1, 1): (1,)})
xor_gate = SimpleGate(identifier="XOR", num_inputs=2, num_outputs=1, truth_table={(0, 0): (0,), (0, 1): (1,), (1, 0): (1,), (1, 1): (0,)})
xnor_gate = SimpleGate(identifier="XNOR", num_inputs=2, num_outputs=1, truth_table={(0, 0): (1,), (0, 1): (0,), (1, 0): (0,), (1, 1): (1,)})
nor_gate = SimpleGate(identifier="NOR", num_inputs=2, num_outputs=1, truth_table={(0, 0): (1,), (0, 1): (0,), (1, 0): (0,), (1, 1): (0,)})

class AlLogic:

    def interpret(self, model):

        # model is an instance of Program
        for instruction in model.instructions:

            if instruction.__class__.__name__ == "Import":
                file = instruction.path
                
                if file == 'stl':
                    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'stl.al')

                else:
                    #append extension
                    file.directory[-1] = f"{file.directory[-1]}.{file.extension}"
                    # Join the components into the full path
                    full_path = os.path.join(*file.directory)

                import_logic = AlLogic()
                import_model = allogic_mm.model_from_file(full_path)
                import_logic.interpret(import_model)

            if instruction.__class__.__name__ == "Definition":
                gate_name = instruction.name
                num_inputs = instruction.inputs
                num_outputs = instruction.outputs
                gate = ComplexGate(identifier=gate_name, num_inputs=num_inputs, num_outputs=num_outputs)
                defined_gates.update({gate_name: gate})

                for inclusion in instruction.inclusions:

                    if inclusion.gate not in defined_gates:
                        raise LookupError(f"Gate {instruction.circuit} not defined")
                    gate.add_component(defined_gates.get(inclusion.gate), inclusion.identifier)
                for connection in instruction.connections:
                    source_node = connection.source
                    target_node = connection.target
                    gate.connect(source_node.instance, (source_node.side, source_node.index), target_node.instance, (target_node.side, target_node.index))
            
            elif instruction.__class__.__name__ == "Declaration":
                if instruction.gate not in defined_gates:
                    raise LookupError(f"Gate {instruction.gate} not defined")
                         
                circuit = CircuitInstance(instruction.identifier, defined_gates.get(instruction.gate))
                declared_circuits.update({instruction.identifier: circuit})

            
            elif instruction.__class__.__name__ == "Execution":
                if instruction.circuit not in declared_circuits:
                    raise LookupError(f"Gate {instruction.circuit} not declared")

                values = tuple([i for i in instruction.values])
                circuit = declared_circuits.get(instruction.circuit)
                circuit.update_inputs(values)
                print(circuit)




if __name__ == "__main__":
    # Check the number of arguments (argc) passed to the script
    if len(sys.argv) < 2:
        print("Usage: python AlLogic.py <input_file>")
        sys.exit(1)

    # Access the file path argument (argv)
    input_file = sys.argv[1]

    # Call the main function with the input file argument
    allogic_mm = metamodel_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'AlLogic.tx'))
    alllogic_model = allogic_mm.model_from_file(input_file)
    logic = AlLogic()
    logic.interpret(alllogic_model)