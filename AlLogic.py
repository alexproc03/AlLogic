# from textx import metamodel_from_file
# allogic_mm = metamodel_from_file('AlLogic.tx')
# alllogic_model = allogic_mm.model_from_file('test.al')

defined_circuits = {}


class Gate:
    def __init__(self, num_inputs, num_outputs):
        self.inputs = num_inputs
        self.outputs = num_outputs


class SimpleGate(Gate):
    def __init__(self, num_inputs, num_outputs, truth_table):
        super().__init__(num_inputs, num_outputs)
        self.truth_table = truth_table

class ComplexGate(Gate):
    def __init__(self, num_inputs, num_outputs):
        super().__init__(num_inputs, num_outputs)
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
            # Initialize sub-circuits
            for identifier, sub_gate in gate.components.items():
                self.sub_circuits[identifier] = CircuitInstance(identifier, sub_gate)

            for from_gate, from_node, to_gate, to_node in gate.connections:
                circuit_from = self if from_gate == "this"  else self.sub_circuits.get(from_gate)
                circuit_to = self if to_gate == "this" else self.sub_circuits.get(to_gate)
                node_object_from = circuit_from.input_nodes[from_node[1]] if from_node[0] == 'in' else circuit_from.output_nodes[from_node[1]]
                node_object_to = circuit_to.input_nodes[to_node[1]] if to_node[0] == 'in' else circuit_to.output_nodes[to_node[1]]
                node_object_to.set_source(node_object_from)
                node_object_from.dependents.append(node_object_to)

            for from_gate, from_node, to_gate, to_node in gate.connections:
                circuit_from = self if from_gate == "this"  else self.sub_circuits.get(from_gate)
                circuit_to = self if to_gate == "this" else self.sub_circuits.get(to_gate)
                node_object_from = circuit_from.input_nodes[from_node[1]] if from_node[0] == 'in' else circuit_from.output_nodes[from_node[1]]

    def __str__(self):
        return f'{self.name}, {super().__str__()}'



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
            output_values = self.type.truth_table.get(input_values, (0,) * self.type.outputs)
            for node, value in zip(self.output_nodes, output_values):
                node.set_value(value)
        elif isinstance(self.type, ComplexGate):
            # Propagate logic through sub-components
            for connection in self.type.connections:
                output_gate, output_node, input_gate, input_node = connection
                source_value = self.sub_circuits[output_gate].output_nodes[output_node].value
                self.sub_circuits[input_gate].input_nodes[input_node].set_value(source_value)

            # Evaluate all sub-circuits
            for sub_circuit in self.sub_circuits.values():
                sub_circuit.evaluate()

            # Update top-level outputs
            for i, output_node in enumerate(self.output_nodes):
                dependent_gate = self.sub_circuits[output_node.source]
                output_node.set_value(dependent_gate.get_current_outputs()[i])

# Node can have only 1 source, but multiple dependents
class Node:
    def __init__(self, gate: CircuitInstance):
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



#define simple gates as the "base library"
# AND Gate
and_gate_truth_table = {
    (0, 0): (0,),
    (0, 1): (0,),
    (1, 0): (0,),
    (1, 1): (1,)
}
# OR Gate
or_gate_truth_table = {
    (0, 0): (0,),
    (0, 1): (1,),
    (1, 0): (1,),
    (1, 1): (1,)
}
# NOT Gate
not_gate_truth_table = {
    (0,): (1,),
    (1,): (0,)
}
and_gate = SimpleGate(2, 1, and_gate_truth_table)
defined_circuits.update({'AND':and_gate})
or_gate = SimpleGate(2, 1, or_gate_truth_table)
defined_circuits.update({'OR':or_gate})
not_gate = SimpleGate(1, 1, not_gate_truth_table)
defined_circuits.update({'NOT':not_gate})

and3_gate = ComplexGate(3, 1)
and3_gate.add_component(and_gate, "and0")
and3_gate.add_component(and_gate, "and1")
and3_gate.connect("this", ('in',0), "and0", ('in',0))
and3_gate.connect("this", ('in',1), "and0", ('in',1))
and3_gate.connect("and0", ('out',0), "and1", ('in',0))
and3_gate.connect("this", ('in',2), "and1", ('in',1))
and3_gate.connect("and1", ('out',0), "this", ('out',0))
defined_circuits.update({'AND3':and3_gate})
test = CircuitInstance('test', defined_circuits.get('AND3'))

print('\n\n\n\n\nWeirdgate:')

weird_gate = ComplexGate(3,1)
weird_gate.add_component(and3_gate, 'and')
# weird_gate.add_component(not_gate, 'not')
weird_gate.connect("this", ('in', 0), "and", ('in', 0))
weird_gate.connect("this", ('in', 1), "and", ('in', 1))
weird_gate.connect("this", ('in', 2), "and", ('in', 2))
# weird_gate.connect("this", ('in', 3), "not", ('in', 0))
weird_gate.connect("and", ('out', 0), "this", ('out', 0))
# weird_gate.connect("not", ('out', 0), "this", ('out', 1))

test1 = CircuitInstance('test1', weird_gate)


print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print(test)
# class AlLogic:
#     def __init__(self):
#         circuits = list
#         declarations = list

#     def interpret(self, model):

#         # model is an instance of Program
#         for instruction in model.instructions:

#             if instruction.__class__.__name__ == "Definition":
#                 circuit_name = instruction.name
#                 num_inputs = instruction.inputs
#                 num_outputs = instruction.outputs
#                 circuit = Circuit(num_inputs=num_inputs, num_outputs=num_outputs)
#                 defined_circuits.update({circuit_name, circuit})

#                 for inclusion in model.inclusions:
#                     circuit.add_circuit(name = inclusion.instance, circuit = inclusion.gate)
                
#                 for connection in model.connections:
#                     circuit.connect() #todo make sure these parameters are enough and descriptive
            
#             elif instruction.__class__.__name__ == "Execution":
#                 print('hi')
            
#             elif instruction.__class__.__name__ == "Execution":
#                 target = instruction.circuit
#                 values = [i for i in instruction.values]
#                 circuit = defined_circuits.get(target)
#                 circuit.execute(values)

# logic = AlLogic()
# logic.interpret(alllogic_model)