from itertools import combinations


class Node:
    """This class represent a Node of a binary a decision tree that represents either a
        symptom or an illness if it's a leaf"""

    def __init__(self, data, pos=None, neg=None):
        self.data = data
        self.positive_child = pos
        self.negative_child = neg

    def get_p(self):
        return self.positive_child

    def get_n(self):
        return self.negative_child

    def get_data(self):
        data = self.data
        return data

    def is_leaf(self):
        """This function checks if a node instance represents a leaf"""
        if (self.negative_child is None) or (self.positive_child is None):
            return True
        return False


class Record:
    def __init__(self, illness, symptoms):
        self.illness = illness
        self.symptoms = symptoms

    def get_illness(self):
        illness = self.illness
        return illness


def parse_data(filepath):
    with open(filepath) as data_file:
        records = []
        for line in data_file:
            words = line.strip().split()
            records.append(Record(words[0], words[1:]))
        return records


class Diagnoser:
    """This class represent an automatic digonser that using a decision tree  can do some diagnostic actions
        when give it symptoms and ilnesses"""


    def __init__(self, root):
        self.root = root

    def diagnose_rec(self, symptoms, root):
        """The main recursive function for the  method  diagnose"""
        if root.is_leaf():
            # Base case
            return root.get_data()
        elif root.get_data() in symptoms:
            # Current symptom is in our symptoms so we"ll take left
            return self.diagnose_rec(symptoms, root.get_p())
        else:
            # Current symptom isn't in our symptoms so we"ll take right
            return self.diagnose_rec(symptoms, root.get_n())

    def diagnose(self, symptoms):
        """This method returns the illness that an instance tree will find with given symptoms"""
        diagnosis = self.diagnose_rec(symptoms, self.root)
        return diagnosis

    def calculate_success_rate(self, records):
        """This method calculates the ratio between the successes and fails of an instance tree
         trying to diagnose the illness of every record by its symptoms"""
        success_counter = 0
        for record in records:
            if self.diagnose(record.symptoms) == record.get_illness():
                # We got a success by def
                success_counter += 1
        success_rate = success_counter / len(records)
        return success_rate

    def all_illnesses(self):
        """This method returns a sorted non duplicates list that contains the content
         of all leafs of an instance tree"""
        illnesses_lst = self.get_illnesses_lst([], self.root)
        sorted_illnesses = sorted(illnesses_lst, key=illnesses_lst.count, reverse=True)
        no_duplicates_illnesses = sorted(set(sorted_illnesses), key=sorted_illnesses.index)
        return no_duplicates_illnesses

    def get_illnesses_lst(self, lst, root):
        """This function is helper function of "all_illnesses" method , which return a list of all leafs content"""
        if root.is_leaf():
            # Base case when we got to a leaf so we"ll add it to our list
            lst.append(root.get_data())
        else:
            # Continue to look for leafs , in both right and left side
            self.get_illnesses_lst(lst, root.get_n())
            self.get_illnesses_lst(lst, root.get_p())
        return lst

    def most_rare_illness(self, records):
        """This method finds the illness that was found the fewest times(or zreo times=>not found) by
             an instance tree trying to diagnose the illness of every record by its symptoms"""
        illnesses_lst = self.all_illnesses()
        for record in records:
            illnesses_lst.append(self.diagnose(record.symptoms))
        sorted_illnesses = sorted(illnesses_lst, key=illnesses_lst.count)
        no_duplicates_illnesses = sorted(set(sorted_illnesses), key=sorted_illnesses.index)
        return no_duplicates_illnesses[0]

    def paths_to_illness(self, illness):
        """This method finds list of all paths to a given leaf/illness in terms of True=Left and False=Right"""
        if self.paths_to_illness_rec(illness, self.root, [], []):
            return self.paths_to_illness_rec(illness, self.root, [], [])
        return []

    def paths_to_illness_rec(self, illness, root, lst1, lst2):
        """This recusive function is helper of the method "paths_to_illness"""
        if root.is_leaf():
            # Base case
            if root.get_data() == illness:
                # If we got the wanted illness we will add the path till there to our list
                lst1 = lst1[:]
                lst2.append(lst1)
            return
        lst1.append(False)
        self.paths_to_illness_rec(illness, root.get_n(), lst1, lst2)  # Continue search right way
        lst1.pop()  # Backtrack
        lst1.append(True)
        self.paths_to_illness_rec(illness, root.get_p(), lst1, lst2)  # Continue search left way
        lst1.pop()  # Backtrack
        return lst2


def build_tree(records, symptoms):
    """This function create a tree which its nodes are the given symptoms and its leafs are the illnesses that are
    most statistically suitable among illnesses in the records that their symptoms includes the data of
    all the nodes which we said "Yes" and not includes all the nodes we said "No"
     """
    return build_tree_rec(symptoms, records, 0, [])


def build_tree_rec(symptoms, records, s_i, path):
    """This recursive function is helper of the function build_tree"""
    if s_i == len(symptoms):
        # Base case when we got to the a leaf
        return Node(find_illnesses(symptoms, records, path))
    path.append(True)
    pos = build_tree_rec(symptoms, records, s_i + 1, path)  # Continue build left way
    path.pop()  # Backtrack
    path.append(False)
    neg = build_tree_rec(symptoms, records, s_i + 1, path)  # Continue build right way
    path.pop()  # Backtrack
    return Node(symptoms[s_i], pos, neg)


def find_illnesses(symptoms, records, path):
    """This function finds the most statistically suitable illnesses among illnesses in the records that
    their symptoms includes the data of all the nodes which we said "Yes" and not includes all the nodes we said "No"""
    fit_illnesses_lst = []
    for record in records:
        for i in range(len(path)):
            if (symptoms[i] in record.symptoms) != path[i]:
                # Make sure we don't refer to records which their symptoms includes "NO"
                break
        else:
            # Take potential illnesses
            fit_illnesses_lst.append(record.get_illness())
    if not fit_illnesses_lst:
        # In case no potential illnesses were found we will take the illness of the first record
        return records[0].get_illness()
    most_common_illnesses_lst = sorted(fit_illnesses_lst, key=fit_illnesses_lst.count, reverse=True)
    return most_common_illnesses_lst[0]


def optimal_tree(records, symptoms, depth):
    """This function returns the tree with highest chances of
    success while asking of exactly k symptoms from symptoms when k is equal to "depth"""
    depth_size_symptoms = list(combinations(symptoms, depth))
    optimal_tree = build_tree(records, depth_size_symptoms[0])  # Assume the tree with first symptoms set is the optimal

    dr = Diagnoser(optimal_tree)
    best_rate = dr.calculate_success_rate(records)  # Optimal tree rate is the best by def, cause' we assumed so

    for symptoms_gruop in depth_size_symptoms:
        # Every time we"ll update the optimal tree to be the optimal so far by comparing all trees success rates
        dr = Diagnoser(build_tree(records, symptoms_gruop))
        if dr.calculate_success_rate(records) >= best_rate:
            optimal_tree = dr.root
            best_rate = dr.calculate_success_rate(records)

    return optimal_tree


if __name__ == "__main__":

    # Manually build a simple tree.
    #                cough
    #          Yes /       \ No
    #        fever           healthy
    #   Yes /     \ No
    # influenza   cold

    flu_leaf = Node("influenza", None, None)
    cold_leaf = Node("cold", None, None)
    inner_vertex = Node("fever", flu_leaf, cold_leaf)
    healthy_leaf = Node("healthy", None, None)
    root = Node("cough", inner_vertex, healthy_leaf)

    diagnoser = Diagnoser(root)

    # Simple test
    diagnosis = diagnoser.diagnose(["cough"])
    if diagnosis == "cold":
        print("Test passed")
    else:
        print("Test failed. Should have printed cold, printed: ", diagnosis)

    records = parse_data("/Users/benmorad/Downloads/Ex11 Files-20181226/tiny_data.txt")
    diagnoser.root = root
    print(diagnoser.paths_to_illness("cold"))

