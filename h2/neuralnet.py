from lib import arff
from random import shuffle
import sys, helpers, math

#helpers
load_data = helpers.load_data
homogenous_check = helpers.homogenous_check
get_attributes = helpers.get_attributes
get_class_counts = helpers.get_class_counts
get_arguments = helpers.get_arguments

# no hidden units or momentum are used
# one sigmoid output only, since the problem is binary 
# one input per numeric feature (e.g. 60x in the current example)
# All weights and the bias parameter are initialized to the value 0.1
# Stochasic gradient descent is used to minimize squared error
def sigmoid(x):
  # run the sigmoid function
  return 1.0 / (1.0 + math.exp( - x))


def init_weights(num_features):
  weights = []
  # initialize all features to .1, except class which we exclude
  for x in range(num_features):
    weights.append(0.1)

  return weights


# What is the 'actual' pre-determined class label?
def get_actual(actual, class_labels):
  if actual[-1] == class_labels[0]:
    # we expected rock
    return 0.0
  else:
    # we expected mine
    return 1.0 # we can assume the 2nd class value is positive


# translate sigmoid_output into a prediction value
# in terms of accuracy, we look at 0 or 1
def get_thresholded_value(sigmoid_output):
  if value > 0.5:
    return 1.0
  else:
    return 0.0

def compute_output(bias, weights, actual):
  # add the bias
  net = bias
  # add the rest of the weighted units
  for i in range(len(actual) - 1):
    net += weights[i] * actual[i]
  # forward propagate net to the next layer (the sigmoid)
  o = sigmoid(net)
  return o

def stochastic_gradient_descent(learn_rate, actual, bias, weights, class_labels):
  # stochastic gradient descent algorithm:
  # for each (x(d), y(d)) in the training set
  #   input x(d) to the network & compute output o(d)
  #    calculate the error E(w) = 1/2 (y(d) - o(d))^2
  #    calculate the gradient
  #    VE(w) = [dE/dw_0, dE/dw_1, ...] 
  #    update the weights
  #    /\w = - learn_rate * VE(w)

  # save the old weights to test after.....
  old_weights = list(weights)

  o = compute_output(bias, weights, actual)
  # get the actual result ('rock' or 'mine')
  y = get_actual(actual, class_labels)
  # apply "Delta Rule" [get the error E(w)]: sum up 1/2 the squared error distances
  error = math.pow((y - o), 2) / 2.0
  # print 'output o:%f, actual y:%f, dif:%f, sq_err:%f' % (o, y, (y - o), error)
  
  # calculate the gradient
  p_derivative_err_out = - (y - o)
  # the derivative of the error with respect to the weight
  p_derivative_out_net = o * (1 - o)
  
  # print 'p_derivative_err_out:%f, p_derivative_out_net:%f' %(p_derivative_err_out, p_derivative_out_net)
  # print actual

  # calculate the partial derivative for each weight
  for i in range(len(actual) - 1):
    X_i = actual[i]
    # the partial error derivative with respect W_i
    error_derivative_w = p_derivative_err_out * p_derivative_out_net * X_i
    # now we can update the weight for this item
    weight_delta = - learn_rate * error_derivative_w
    new_weight =  weights[i] + weight_delta
    # new_X_i = actual[i] * new_weight
    # print 'X_i:%f, actual:%f, weight:%f, weight_delta:%f, error_derivative_w:%s' %(X_i, actual[i], weights[i], weight_delta, error_derivative_w)
    # print 'weight before:%f, weight after:%f, X_i:%f, new X_i:%f'  % (weights[i], new_weight, X_i, new_X_i)
    weights[i] = new_weight

  # update the bias
  error_derivative_w = p_derivative_err_out * p_derivative_out_net * 1
  # old_bias = bias
  bias += - learn_rate * error_derivative_w
  # print 'old bias:%f, bias: %f, error_derivative_w:%f' % (old_bias, bias, error_derivative_w)

  # if bias != 0.1:
  #   # let's check before / after error on the same set!
  #   old_output = compute_output(old_bias, old_weights, actual)
  #   new_output = compute_output(bias, weights, actual)
  #   expected = get_actual(actual, class_labels)
  #   print 'old_output:%f, new_output:%f, expected:%f' % (old_output, new_output, expected)
  #   exit(0)
  # else:
  #   pass

  return bias, weights


def split_instances(training_set, class_labels):
  """ split training set into positive / negative samples """
  pos_instances = []
  neg_instances = []

  for instance in training_set:
    class_type = get_actual(instance, class_labels)
    if class_type > 0.5:
      pos_instances.append(instance)
    else:
      neg_instances.append(instance)

  return pos_instances, neg_instances


def stratified_k_cross_folds(pos_instances, neg_instances, k_folds):
  pos_count = len(pos_instances)
  neg_count = len(neg_instances)
  
  # determine which count is less; this will determine fold_size
  n_fold_size = int( math.ceil( neg_count / float(k_folds) ) )
  p_fold_size = int( math.ceil( pos_count / float(k_folds) ) )

  # randomize
  shuffle(pos_instances)
  shuffle(neg_instances)

  # For stratified cross-validation, the training set will have an equal number 
  # of patterns from each class (otherwise it isn't stratified)
  k_cross_folds = []
  i = 0
  j = 0
  for x in range(k_folds):
    curr_fold = []
    for y in range(p_fold_size):
      if i < pos_count:
        curr_fold.append(pos_instances[i])
        i += 1
      else:
        pass

    for z in range(n_fold_size):
      if j < neg_count:
        curr_fold.append(neg_instances[j])
        j += 1
      else:
        pass

    shuffle(curr_fold)
    k_cross_folds.append(curr_fold)

  data = []
  for fold in k_cross_folds:
    for row in fold:
      data.append(row)

  # print len(data)
  # exit(0)
  return k_cross_folds

def validation_test(bias, weights, validation_set, class_labels):
  """ determine the error of the current weights vs the validation set"""

  # get the total error for this entire validation set
  error = 0
  for actual in validation_set:
    o = compute_output(bias, weights, actual)
    y = get_actual(actual, class_labels)
    # print 'actual result:' + str(y)
    # print 'sigmoid:' + str(o)
    error += math.pow((y - o), 2) / 2.0

  return error


def get_prediction(bias, weights, actual, class_labels):
  net = bias
  # add the rest of the weighted units
  for i in range(len(actual) - 1):
    net += weights[i] * actual[i]

  o = sigmoid(net)
  # greater than 0.5 == positive
  if o > 0.5:
    return class_labels[1], o
  else:
    return class_labels[0], o

def generate_hashmap(k_cross_folds):
  # generate a hashtable for lookups
  data_lookup = {}
  fold_number = 0
  for fold in k_cross_folds:
    fold_number += 1
    for row in fold:
      key = ''
      for item in row:
        key += str(item)
      data_lookup[key] = {'fold_number': fold_number}

  return data_lookup

def print_output(k_cross_folds, bias, weights, data, class_labels):
  """ print one line per instance in the same order as data file """
  # generate a hashtable for lookups
  data_lookup = generate_hashmap(k_cross_folds)

  # for key in data_lookup:
  #   print data_lookup[key].get('fold_number')
  correct_count = 0
  total = len(data)
  for row in data:
    # generate the hash key to find this row's fold number
    key = ''
    for item in row:
      key += str(item)

    fold = data_lookup.get(key)
    fold_number = str(fold.get('fold_number'))
    i = int(fold_number) - 1 # switch from fold_number to zero-based index
    fold_number = fold_number.rjust(2, '0')
    predicted, sigmoid = get_prediction(bias[i], weights[i], row, class_labels)
    actual = row[-1]
    print 'fold:%s  predicted:%s  actual:%s  confidence:%.4f' %(fold_number, predicted, actual, sigmoid)
    # was the prediction correct?
    if predicted == actual:
      correct_count += 1
    else:
      pass

  c = correct_count
  t = total
  print 'test set: predicted %d correctly. %d/%d = %f accuracy' % (c, c, t, c / float(t))

  # get training set accuracy...
  # run each generated set of weights vs the training set the weights were generated with
  training_set = []
  total = 0
  training_set_correct = 0
  n = len(k_cross_folds)

  for v in range(n):
    for i in range(n):
      if i == v:
        pass # ignore the test set!
      else:
        for row in k_cross_folds[i]:
          predicted, sigmoid = get_prediction(bias[v], weights[v], row, class_labels)
          actual = row[-1]
          if predicted == actual:
            training_set_correct += 1
          else:
            pass
          total +=1

  t = total
  c = training_set_correct
  print 'training sets: predicted %d correctly. %d/%d = %f accuracy' % (c, c, t, c / float(t))


def train_curr_fold(training_set, l, bias, weights, class_labels):
  errors = 0
  for instance in training_set:
    # training_set.append(fold)
    bias, weights = stochastic_gradient_descent(l, instance, bias, weights, class_labels)

  return bias, weights


def print_roc_curve(bias, weights, data, class_labels, k_cross_folds):
  """ The ROC curve is a diagnostic tool that plots the proportion of true """
  """ positives against the proportion of false positives for all possible """
  """ values of the threshold parameter."""
  # with the ROC curve we manipulate the threshold, to see where the various breakpoints
  # are where we get a tangible trade-off between false positives/ false negatives
  pos = class_labels[1]
  neg = class_labels[0]
  num_neg, num_pos, TP, FP, FPR, TPR, last_TP = 0, 0, 0, 0, 0, 0, 0
  # instances sorted according to predicted confidence c(i) that each instance is positive
  # get number of negative/positive instances in the test set TP=0, FP=0!
  for row in data:
    if row[-1] == class_labels[1]:
      num_pos += 1
    else:
      num_neg += 1
  
  data_lookup = generate_hashmap(k_cross_folds)
  # determine confidence for each row
  results = []
  for row in data:
    # generate a hash key to find this row's fold number
    key = ''
    for item in row:
      key += str(item)
    fold = data_lookup.get(key)
    i = int(fold.get('fold_number')) - 1 # switch from fold_number to zero-based index
    predicted, sigmoid = get_prediction(bias[i], weights[i], row, class_labels)
    actual = row[-1]
    item = { 'data': row, 'predicted': predicted, 'actual': actual, 'confidence': sigmoid }
    results.append(item)
  # sort by confidence, ascending
  results = sorted(results, key=lambda k: k['confidence']) 
  # reverse the order
  results.reverse()

  # for i in range(len(results)):
  #   print 'i:' + str(i) + ' conf:' + str(results[i].get('confidence')) + ' actual:' + str(results[i].get('actual'))
  # exit(0)

  # keep reducing the threshold to find new plot points
  output = []
  # our first point is always zero
  output.append({'FPR':0, 'TPR':0})

  for i in range(1, len(results)):
    # find thresholds where there is a pos instance on high side, neg instance on low side
    # predicted is negative
    curr_conf = results[i].get('confidence')
    prev_conf = results[i - 1].get('confidence')

    if curr_conf != prev_conf and results[i].get('actual') == neg and TP > last_TP:
      FPR = FP / float(num_neg)
      TPR = TP / float(num_pos)
      # add the new coordinate
      output.append({'FPR':FPR, 'TPR':TPR})
      last_TP = TP

    # if this was the threshold, what would happen?
    if results[i].get('actual') == pos:
      TP += 1
    else:
      FP += 1

  FPR = FP / num_neg
  TPR = TP / num_pos
  
  # output plot points
  for rs in output:
    print 'FPR: %f, TPR: %f'%(rs.get('FPR'), rs.get('TPR'))

  # for rs in data:
  #   print 'actual:%s, predicted:%s, confidence:%f'%(rs['actual'], rs['predicted'], rs['confidence'])


def main(args):
  """usage neuralnet.py <data-set-file> n l e"""
  """ n = the number of folds for cross validation """
  """ l = the learning rate """
  """ e = the number of training epochs """

  train_set_file, n, l, e = get_arguments(args)
  # n = 10  # number of cross validation folds
  # l = 0.1 # learning rate
  # e = 100 # training epochs
  if n < 2:
    raise ValueError('This K-Fold program expects n >= 2 (i.e. 2x folds minimum)')
  else:
    pass

  # arff_file = load_data(train_set_file)
  arff_file = load_data('examples/sonar.arff')
  attributes = get_attributes(arff_file['attributes'])
  class_labels = attributes.get('Class').get('options')
  data = arff_file['data']

  the_weights = init_weights(len(attributes))
  the_bias = 0.1

  weights = []
  bias = []
  for v in range(n):
    weights.append(list(the_weights))
    bias.append(the_bias)

  # run the current epoch (one pass through the entire training set)
  pos_instances, neg_instances = split_instances(data, class_labels)
  k_cross_folds = stratified_k_cross_folds(pos_instances, neg_instances, n)

  # run program for the specified number of epochs
  for epoch in range(e):
    # we only update the weights once per epoch; we cross-validate all folds,
    # then the fold that 'wins' becomes the update
    for v in range(n):
      # print 'on iteration k = %s of k-folds: %s' %(v, n)
      # get the current validation set
      validation_set = k_cross_folds[v]
      # loop through each training set, skipping the validation set
      for i in range(n):
        if i == v:
          pass # don't train on the validation set!!
        else:
          # run the current set; clone the weights (we don't want to update them accidentally!)
          bias[v], weights[v] = train_curr_fold(k_cross_folds[i], l, bias[v], weights[v], class_labels)

  print_output(k_cross_folds, bias, weights, data, class_labels)
  # print_roc_curve(bias, weights, data, class_labels, k_cross_folds)

  # display weight issue:
  # print 'bias %.2f' %(bias[0])
  # for i in range(len(weights[0])):
  #   print 'weight %02d %.2f' %(i, weights[0][i])

if __name__ == "__main__":
  main(sys.argv)

