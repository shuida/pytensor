from pytensor.network.optimizer import *

class Trainer:

    def __init__(self, model):
        """
        A trainer example

        :param model:
        """

        self.model = model
        self.optimizer = SGD(self.model.parameter)

    def train(self, x_train, y_train, x_test=None, y_test=None, epoch=40, iteration=10000):

        for ii in range(epoch):

            loss = 0.0

            for i in range(len(x_train)):

                # extract data set
                input_variables = Variable([x_train[i]])
                target_variable = Variable([y_train[i]])

                # forward
                self.model.forward(input_variables)

                # loss
                loss += self.model.loss(target_variable)

                # backward
                self.model.backward()

                self.optimizer.update()

            accuracy = self.test(x_test, y_test)
            print("\repoch {}: loss {}, acc {}".format(ii, loss, accuracy), end='')


    def test(self, x_test, y_test):

        acc_cnt = 0.0
        all_cnt = len(x_test)

        for i in range(len(x_test)):

            v = Variable([x_test[i]])
            output_variable = self.model.forward(v)

            y = np.argmax(output_variable.value[0])
            if y == y_test[i]:
                acc_cnt += 1.0

        return acc_cnt/all_cnt
