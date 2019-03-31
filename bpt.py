import bisect
import itertools
import operator
import sys

class _BNode(object):

    def __init__(self, bptree, elements=None, descendants=None):
        self.bptree = bptree
        self.elements = elements or []
        self.descendants = descendants or []

######################################################################################################

    def lateral(self, parent, parent_index, dest, dest_index):
        if parent_index > dest_index:
            dest.elements.append(parent.elements[dest_index])
            parent.elements[dest_index] = self.elements[0]
            del self.elements[0]
            if self.descendants:
                dest.descendants.append(self.descendants[0])
                del self.descendants[0]
        else:
            dest.elements.insert(0, parent.elements[parent_index])
            parent.elements[parent_index] = self.elements[-1]
            del self.elements[-1]
            if self.descendants:
                dest.descendants.insert(0, self.descendants[-1])
                del self.descendants[-1]

############################################################################################

    # def split_node(self):
    #     center = int(len(self.elements)/2)#// 2
    #     medn = self.elements[center]
    #     sibl = type(self)(self.bptree,self.elements[center + 1:],self.descendants[center + 1:])
    #     self.elements = self.elements[:center]
    #     self.descendants = self.descendants[:center + 1]
    #     return sibl, medn


#############################################################################################
    def split(self):
        # sib,med = self.split_node()
        # return self.split_node()
        center = int(len(self.elements)/2)#// 2
        medn = self.elements[center]
        sibl = type(self)(self.bptree,self.elements[center + 1:],self.descendants[center + 1:])
        self.elements = self.elements[:center]
        self.descendants = self.descendants[:center + 1]
        return sibl, medn

#######################################################################################################

    def contract(self, ancestors):
        parent = None
        totalAncestors=len(ancestors)
        left_sib=None
        right_sib=None

        # check if there is a space in destination node
        if ancestors:
            parent=ancestors[-1][0]
            parent_index = ancestors[-1][1]
            del ancestors[-1]
            if parent_index:
                left_sib = parent.descendants[parent_index - 1]
            if parent_index < len(parent.descendants)-1:
                right_sib = parent.descendants[parent_index + 1]

            #if left child have space put key in it
            if left_sib and len(left_sib.elements) < self.bptree.degree:
                self.lateral(parent, parent_index, left_sib, parent_index - 1)
                return

            #if right child have space put key in it
            if right_sib and len(right_sib.elements) < self.bptree.degree:
                self.lateral(parent, parent_index, right_sib, parent_index + 1)
                return

        # split the parent node since no vacancy in child
        center = int(len(self.elements)/2) #// 2
        sibl, push = self.split()

        if not parent:
            parent, parent_index = self.bptree.BRANCH(self.bptree, descendants=[self]), 0
            self.bptree._root = parent

        parent.elements.insert(parent_index, push)
        parent.descendants.insert(parent_index + 1, sibl)
        if len(parent.elements) > parent.bptree.degree:
            parent.contract(ancestors)

############################################################################################################################


############################################### class BPlus leaf ########################################################

class _BPlusLeaf(_BNode):

    def __init__(self, bptree, elements=None, data=None, next=None):
        self.bptree = bptree
        self.elements = elements or []
        self.data = data or []
        self.next = next


#######################################################################################################

    def insert(self, index, key, data, ancestors):
        self.elements.insert(index, key)
        self.data.insert(index, data)
        if  len(self.elements) > self.bptree.degree:
            self.contract(ancestors)

#######################################################################################################

    def lateral(self, parent, parent_index, dest, dest_index):
        if parent_index <= dest_index:
            dest.elements.insert(0, self.elements[-1])
            del self.elements[-1]
            dest.data.insert(0, self.data[-1])
            del self.data[-1]
            parent.elements[parent_index] = dest.elements[0]
        else:
            dest.elements.append(self.elements[0])
            del self.elements[0]
            dest.data.append(self.data[0])
            del self.data[0]
            parent.elements[dest_index] = self.elements[0]
            

#######################################################################################################

    def split(self):
        center = int(len(self.elements)/2)# // 2
        medn = self.elements[center - 1]
        sibl = type(self)(self.bptree,self.elements[center:],self.data[center:],self.next)
        self.elements = self.elements[:center]
        self.data = self.data[:center]
        self.next = sibl
        return sibl, sibl.elements[0]

########################################### class BTree ############################################################

class BTree(object):
    BRANCH = LEAF = _BNode

    def __init__(self, degree):
        self.degree = degree
        self._bottom = self.LEAF(self)
        self._root = self.LEAF(self)
#######################################################################################################

    def getPath(self, item,current,ancestors):
        # current = self._root
        # ancestors = []
        # while getattr(current, "descendants", None):
        #     index = bisect.bisect_left(current.elements, item)
        #     ancestors.append((current, index))
        #     if index < len(current.elements) and current.elements[index] == item:
        #         return ancestors
        #     current = current.descendants[index]

        # index = bisect.bisect_left(current.elements, item)
        # ancestors.append((current, index))
        # present = index < len(current.elements)
        # present = present and current.elements[index] == item

        # return ancestors
        # ancestors = []
        if getattr(current, "descendants", None):
            # index = bisect.bisect_left(current.elements, item)
            #find position of item in current elements
            keys=sorted(current.elements)
            index = 0
            for x in keys:
                if x < item:
                    index += 1
            ancestors.append((current, index))
            if index < len(current.elements) and current.elements[index] == item:
                return ancestors
            # current = current.descendants[index]
            return super(BPlusTree, self).getPath(item,current.descendants[index],ancestors)
        else:
            # index = bisect.bisect_left(current.elements, item)
            keys=sorted(current.elements)
            index = 0
            for x in keys:
                if x < item:
                    index += 1
            ancestors.append((current, index))
            # present = index < len(current.elements)
            # present = present and current.elements[index] == item
            return ancestors


############################################## class Bplus Tree #########################################################

class BPlusTree(BTree):
    LEAF = _BPlusLeaf

    def _find_key(self, key):
        ancestors=self.getPath(key)
        node = ancestors[len(ancestors)-1][0]
        index = ancestors[len(ancestors)-1][1]
        if index == len(node.elements):
            if node.next:
                return node.next.data[0]
                # node, index = node.next, 0
            else:
                return False
        return node.elements[index]
        # while node.elements[index] == key:
        #     yield node.data[index]
        #     index += 1
        #     if index == len(node.elements):
        #         if node.next:
        #             node, index = node.next, 0
        #         else:
        #             return

#######################################################################################################

    def getPath(self, item):
        path = super(BPlusTree, self).getPath(item,self._root,[])
        node =path[len(path)-1][0]
        index = path[len(path)-1][1]
        try:
            while True:
                # if hasattr(node, "descendants"):
                node = node.descendants[index]
                # index = bisect.bisect_left(node.elements, item)
                keys=sorted(node.elements)
                index = 0
                for x in keys:
                    if x < item:
                        index += 1
                ancestor=(node, index)
                path.append(ancestor)
        except AttributeError:
            #catch descendent/children not found exception and exits (break the loop)
            pass
        return path


#######################################################################################################


    def insert(self, key, data):
        path = self.getPath(key)
        totalAncestors=len(path)

        # get node and its index
        node= path[totalAncestors-1][0]
        index = path[totalAncestors-1][1]

        del path[totalAncestors-1]
        node.insert(index, key, data, path)

#######################################################################################################

# Count number of elements in between pair of keys
    def range_query(self, upper_bound, lower_bound):
        # keys=bpt.get_keys()
        allKeys = []
        node = self._root
        # traverse to left most node
        try:
            while True:
                node = node.descendants[0]
        except AttributeError:
            pass
        # get all elements through the linked list elements=keys=values
        while node:
            allKeys+=node.elements
            node = node.next
        keys=allKeys
        keys=sorted(keys)
        # keys=sorted(bpt.get_keys())
        count = 0
        for x in keys:
            if lower_bound <= x <= upper_bound:
                count += 1
        print(count)
        # print(bisect.bisect_right(keys,int(upper_bound))-bisect.bisect_left(keys,int(lower_bound)))

##############################################################################################################

# Count number of occurences of key in tree
    def count_query(self,key):
        allKeys = []
        node = self._root
        # traverse to left most node until node have descendents/childeren
        try:
            while True:
                node = node.descendants[0]
        except AttributeError:
            pass
        # get all elements through the linked list elements=keys=values
        while node:
            allKeys+=node.elements
            node = node.next
        keys=allKeys
        # keys=bpt.get_keys()
        count = 0
        for x in keys:
            if key==x:
                count += 1
        print(count)
        # print(bisect.bisect_right(keys,int(key))- bisect.bisect_left(keys,int(key)))

################################################################################################################

# Check if given key exists in tree
    def find_query(self,key):
        # s= next(self._find_key(key),None)
        # if s==None:
        #     print('NO')
        # else:
        #     print('YES')
        # if next(self._find_key(key),None):
        if self._find_key(key):
            print('YES')
        else:
            print('NO')


#######################################################################################################

    # def get_keys(self):
    #     node = self._root
    #     while hasattr(node, "descendants"):
    #         node = node.descendants[0]

    #     temp = []

    #     while node:
    #         for pair in zip(node.elements, node.data):
    #             temp.append(pair)
    #         node = node.next
    #     return list(map(operator.itemgetter(0), temp))

#################################################################################################
def insert(tokens):
    key=int(tokens[1])
    value=int(tokens[1])
    bpt.insert(key,value)

def find(tokens):
    key=int(tokens[1])
    bpt.find_query(key)

def count(tokens):
    key=int(tokens[1])
    bpt.count_query(key)

def range(tokens):
    high=int(tokens[2])
    low=int(tokens[1])
    bpt.range_query(high,low)


def readFile(filename):
    f=open(filename, "r")
    for x in f:
        tokens=x.split()
        opcode=tokens[0].lower()
        if opcode=='insert':
            insert(tokens)
        elif opcode=='find':
            find(tokens)
        elif opcode=='count':
            count(tokens)
        elif opcode=='range':
            range(tokens)
            

#######################################################################################################

degree = 10
bpt = BPlusTree(degree)

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print("Arguments not correct expected 3 (filename, M, B)")
        sys.exit()
    filename=sys.argv[1]
    M=int(sys.argv[2])
    B=int(sys.argv[3])
    readFile(filename)
