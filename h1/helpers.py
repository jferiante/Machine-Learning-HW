from lib import arff 

# turn attributes into something manageable
def get_attributes(attr_data):
  attributes = {}
  for key in attr_data:
    attributes[str(key[0])] = key[1]

  return attributes
  
def homogenous_check(data, class_labels, negative, positive):
  # are all examples one type? (all pos / all neg)
  positive_found = False
  negative_found = False
  
  for row in data:
    if row[-1] == negative:
      negative_found = True
    elif row[-1] == positive:
      positive_found = True
    else:
      pass
    if negative_found and positive_found:
      return False, None

  if negative_found and not positive_found:
    # data[0][-1] is the class
    return True, negative
  elif positive_found and not negative_found:
    return True, positive
  else:
    # this should never happen
    return False, None


def load_data(path = None):
  if not path:
    raise ValueError('A valid path to training data must be be specified')
    # fp = open('examples/heart_test.arff')
    # fp = open('examples/heart_train.arff')
    # fp = open('examples/diabetes_test.arff')
    # fp = open('examples/diabetes_train.arff')
  else:
    fp = open(path)
    
  data = arff.load(fp)
  return data;


def dump_attributes(data):
  #attributes is a python list - stepping, slicing, etc.
  #bracket = list
  #paren = tuple
  #brace = dict
  attributes = data['attributes']
  # attribute types: NUMERIC, REAL, INTEGER, STRING, and NOMINAL
  #  NUMERIC, REAL, INTEGER == convert to int
  # list == NOMINAL
  
  # Class items
  # print attributes[-1][1][0]
  # print attributes[-1][1][1]

  # blah = [1,2,3]
  # blah2 = (1,2,3)
  # print attributes[0]
  # print attributes[1]
  # print attributes[2]
  # print attributes[3]

  # print blah
  # print blah2
  # return 
  for key in attributes:
    if type(key[0]) is unicode and type(key[1]) is unicode:
      print key[0] + ", " + key[1]
    if type(key[0]) is unicode and type(key[1]) is list:
      options = ''
      count = False
      curr_list = key[1]
      for opt in curr_list:
        if not count:
          options += opt
        else:
          options += ", " + opt
        count = True
      # if key[0] == 'class':
      #  print 'found class!' 
      # else:
      #   pass
      print key[0] + ", nominal: " + options
    # if type([]) is list -- list is array
    # if type({}) is dict -- dict is object
    # if type('') is str or unicode
    # if type(0) is int