from network.base.operation import *

class Add(Operation):

    def forward(self, input_variables):
        """
        Add all variables in the input_variable

        :param input_variables:
        :return:
        """

        self.input_variables = input_variables

        # update dependency
        for input_variable in self.input_variables:
            input_variable.dependency_cnt += 1


        # value for the output variable
        value = np.zeros_like(self.input_variables[0])

        for input_variable in self.input_variables:
            value += input_variable.value

        self.output_variable = Variable(value, input_ops=self)

        return self.output_variable

    def backward(self):
        """
        backward grad into each input variable

        :return:
        """

        for input_variable in self.input_variables:
            input_variable.grad += self.output_variable.grad
            input_variable.backward()


class Multiply(Operation):

    def forward(self, input_variables):
        """
        element multiplication of input_variables

        :param input_variables:
        :return:
        """

        # only multiplication of two elements is supported now
        assert(len(input_variables)==2)

        self.input_variables = input_variables

        # update dependency
        for input_variable in self.input_variables:
            input_variable.dependency_cnt += 1

        # validate both input_variables have same shape
        self.x = input_variables[0]
        self.y = input_variables[1]
        assert(self.x.shape == self.y.shape)

        # value for the output variable
        value = np.multiply(self.x, self.y)
        self.output_variable = Variable(value, input_ops=self)

        return self.output_variable

    def backward(self):
        """
        backward grad into each input variables

        :return:
        """

        # update gradient
        self.x.grad += np.multiply(self.output_variable.grad, self.y.value)
        self.y.grad += np.multiply(self.output_variable.grad, self.x.value)

        # back prop
        for input_variable in self.input_variables:
            input_variable.backward()


class Matmul:

    def forward(self, input_variables):

        # only multiplication of two elements is supported now
        assert(len(input_variables)==2)

        self.input_variables = input_variables

        # update dependency
        for input_variable in self.input_variables:
            input_variable.dependency_cnt += 1

        self.x = input_variables[0]
        self.y = input_variables[1]

        self.input_variable = input_variables
        out = np.dot(self.x.value, self.y.value)

        self.output_variable = Variable(out, input_ops=self)
        return self.output_variable

    def backward(self):

        # update gradient
        self.x.grad += np.dot(self.output_variable.grad, self.y.value.T)
        self.y.grad += np.dot(self.x.value.T, self.output_variable.grad)

        # back prop
        for input_variable in self.input_variables:
            input_variable.backward()


class Relu:
    def __init__(self, name="Relu"):
        self.name = name
        self.mask = None

    def forward(self, input_variable):
        """
        :param input_variable:
        :return:
        """

        # remember input variable
        self.input_variable = input_variable

        # compute mask
        self.mask = (input_variable.value <= 0)

        # create output variable
        out = input_variable.value.copy()
        out[self.mask] = 0
        self.output_variable = Variable(out)

        # return
        return self.output_variable

    def backward(self):
        self.input_variable.grad = self.output_variable.grad
        self.input_variable.grad[self.mask] = 0


class Sigmoid:
    def __init__(self, name='Sigmoid'):
        self.name = name
        self.input_variable = None
        self.output_variable = None

    def forward(self, input_variable):
        self.input_variable = input_variable
        out = sigmoid(self.input_variable.value)

        self.output_variable = Variable(out)
        return self.output_variable

    def backward(self):
        self.input_variable.grad += self.output_variable.grad * (1.0 - self.output_variable.value) * self.output_variable.value


class Tanh:

    def __init__(self, name="Tanh"):
        self.name = name
        self.input_variable = None
        self.output_variable = None

    def forward(self, input_variable):
        self.input_variable = input_variable
        out = np.tanh(self.input_variable.value)

        self.output_variable = Variable(out)
        return self.output_variable

    def backward(self):
        self.input_variable.grad += self.output_variable.grad * (1.0 - self.output_variable.value * self.output_variable.value)


class Affine:
    def __init__(self, input_size, hidden_size, parameter, name='Affine'):
        self.name = name

        self.input_size = input_size
        self.hidden_size = hidden_size

        W_name = self.name + "_W"
        b_name = self.name + "_b"

        self.W = parameter.get_variable(W_name, (input_size, hidden_size))
        self.b = parameter.get_variable(b_name, (hidden_size, ))

    def forward(self, input_variable):
        self.input_variable = input_variable
        out = np.dot(self.input_variable.value, self.W.value) + self.b.value

        self.output_variable = Variable(out)
        return self.output_variable

    def backward(self):
        self.input_variable.grad += np.dot(self.output_variable.grad, self.W.value.T)
        self.W.grad += np.dot(self.input_variable.value.T, self.output_variable.grad)
        self.b.grad += np.sum(self.output_variable.grad, axis=0)