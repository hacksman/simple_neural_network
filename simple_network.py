# -*- coding: utf-8 -*-
# @Time    : 4/19/18 8:40 AM
import random
import math


class NeuralNetwork():
    LEARNING_RATE = 0.5

    def __init__(self, num_inputs, num_hiddens, num_outputs, hidden_layer_weights=None, hidden_layer_bias=None, output_layer_weights=None, output_layer_bias=None):
        self.num_inputs = num_inputs

        self.hidden_layer = NeuronLayer(num_hiddens, hidden_layer_bias)
        self.output_layer = NeuronLayer(num_outputs, output_layer_bias)

        self.init_weights_from_inputs_to_hidden_layer_neurons(hidden_layer_weights)
        self.init_weights_from_hidden_layer_neurons_to_output_layer_neurons(output_layer_weights)

    def init_weights_from_inputs_to_hidden_layer_neurons(self, hidden_layer_weights):
        weight_num = 0
        for h in range(len(self.output_layer.neurons)):
            for i in range(self.num_inputs):
                if not hidden_layer_weights:
                    self.hidden_layer.neurons[h].weights.append(random.random())
                else:
                    self.hidden_layer.neurons[h].weights.append(hidden_layer_weights[weight_num])
                weight_num += 1

    def init_weights_from_hidden_layer_neurons_to_output_layer_neurons(self, output_layer_weights):
        weight_num = 0
        for o in range(len(self.output_layer.neurons)):
            for h in range(len(self.hidden_layer.neurons)):
                if not output_layer_weights:
                    self.output_layer.neurons[o].weights.append(random.random())
                else:
                    self.output_layer.neurons[o].weights.append(output_layer_weights[weight_num])
                weight_num += 1

    def feed_forward(self, inputs):
        hidden_layer_outputs = self.hidden_layer.feed_forward(inputs)
        return self.output_layer.feed_forward(hidden_layer_outputs)

    def train(self, train_inputs, train_outputs):
        self.feed_forward(train_inputs)

        pd_errors_wrt_output_neuron_total_net_input = [0]*len(self.output_layer.neurons)
        for o in range(len(self.output_layer.neurons)):
            pd_errors_wrt_output_neuron_total_net_input[o] = self.output_layer.neurons[o].calculate_pd_error_wrt_total_net_input(train_outputs[o])

        pd_errors_wrt_hidden_neuron_total_net_input = [0] * len(self.hidden_layer.neurons)
        for h in range(len(self.hidden_layer.neurons)):
            d_error_wrt_hidden_neuron_output = 0
            for o in range(len(self.output_layer.neurons)):
                d_error_wrt_hidden_neuron_output += pd_errors_wrt_hidden_neuron_total_net_input[o] * self.output_layer.neurons[o].weights[h]

            pd_errors_wrt_hidden_neuron_total_net_input[h] += d_error_wrt_hidden_neuron_output * self.hidden_layer.neurons[h].calculate_pd_active_wrt_total_net_input()

        for o in range(len(self.output_layer.neurons)):
            for w_ho in range(len(self.output_layer.neurons[o].weights)):

                pd_error_wrt_weight = pd_errors_wrt_output_neuron_total_net_input[o] * self.output_layer.neurons[o].calculate_pd_total_net_input_wrt_weight(w_ho)

                self.output_layer.neurons[o].weights[w_ho] -= self.LEARNING_RATE * pd_error_wrt_weight

        for h in range(len(self.hidden_layer.neurons)):
            for w_ih in range(len(self.hidden_layer.neurons[h].weights)):
                # ∂Eⱼ/∂wᵢ = ∂E/∂zⱼ * ∂zⱼ/∂wᵢ
                pd_error_wrt_weight = pd_errors_wrt_hidden_neuron_total_net_input[h] * self.hidden_layer.neurons[
                    h].calculate_pd_total_net_input_wrt_weight(w_ih)

                # Δw = α * ∂Eⱼ/∂wᵢ
                self.hidden_layer.neurons[h].weights[w_ih] -= self.LEARNING_RATE * pd_error_wrt_weight

    def calculate_total_error(self, training_sets):
        total_error = 0
        for t in range(len(training_sets)):
            training_inputs, training_outputs = training_sets[t]
            self.feed_forward(training_inputs)
            for o in range(len(training_outputs)):
                total_error += self.output_layer.neurons[o].calculate_error(training_outputs[o])
        return total_error


class NeuronLayer():

    def __init__(self, num_neurons, bias):
        self.bias = bias
        self.neurons = []
        for i in range(num_neurons):
            self.neurons.append(Neuron(bias))

    def feed_forward(self, inputs):
        outputs = []
        for neuron in self.neurons:
            outputs.append(neuron.calculate_output(inputs))
        return outputs

    def get_outs(self):
        outputs = []
        for neuron in self.neurons:
            outputs.append(neuron.out_put)
        return outputs


class Neuron():

    def __init__(self, bias):
        self.bias = bias
        self.weights = []

    def calculate_output(self, inputs):
        self.inputs = inputs
        self.out_put = self.activate(self.calculate_total_net_input())
        return self.out_put

    def calculate_total_net_input(self):
        total = 0
        for i in range(len(self.inputs)):
            total += self.weights[i] * self.inputs[i]
        return total + self.bias

    def activate(self, total_net_input):
        return 1/(1+math.exp(-total_net_input))

    def calculate_error(self, target_output):
        return 0.5 * (target_output - self.out_put) ** 2

    # ∂E/∂yⱼ
    def calculate_pd_error_wrt_output(self, target_output):
        return - (target_output - self.out_put)

    # dyⱼ/dzⱼ = yⱼ * (1 - yⱼ)
    def calculate_pd_active_wrt_total_net_input(self):
        return self.out_put * (1 - self.out_put)

    # ∂zⱼ/∂wᵢ = wᵢ
    def calculate_pd_total_net_input_wrt_weight(self, index):
        return self.inputs[index]

    # δ = ∂E/∂zⱼ = ∂E/∂yⱼ * dyⱼ/dzⱼ
    def calculate_pd_error_wrt_total_net_input(self, target_output):
        return self.calculate_pd_error_wrt_output(target_output) * self.calculate_pd_active_wrt_total_net_input()


if __name__ == '__main__':
    nn = NeuralNetwork(2, 2, 2, hidden_layer_weights=[0.15, 0.2, 0.25, 0.3], hidden_layer_bias=0.35, output_layer_weights=[0.4, 0.45, 0.5, 0.55], output_layer_bias=0.6)
    for i in range(10000):
        nn.train([0.05, 0.1], [0.01, 0.99])
        print(i, round(nn.calculate_total_error([[[0.05, 0.1], [0.01, 0.99]]]), 9))


