import sys

class _BNode(object):

    def __init__(self, bptree, keys=None, descendants=None):
        self.bptree = bptree
        if keys:
            self.keys = keys
        else:
            self.keys=[]
        if descendants:
            self.descendants = descendants
        else:
            self.descendants=[]

#############################################################################################
    def split(self):
        center = int(len(self.keys)/2)
        medn = self.keys[center]
        sibl = type(self)(self.bptree,self.keys[center + 1:len(self.keys)],self.descendants[center + 1:len(self.descendants)])
        self.keys = self.keys[0:center]
        self.descendants = self.descendants[0:center + 1]
        return sibl, medn

#######################################################################################################

######################################################################################################

    def lateral(self, parent, parent_index, dest, dest_index):
        if dest_index >=parent_index  :
            dest.keys.insert(0, parent.keys[parent_index])
            parent.keys[parent_index] = self.keys[-1]
            del self.keys[-1]
            if self.descendants:
                dest.descendants.insert(0, self.descendants[-1])
                del self.descendants[-1]
        else:
            dest.keys.append(parent.keys[dest_index])
            parent.keys[dest_index] = self.keys[0]
            del self.keys[0]
            if self.descendants:
                dest.descendants.append(self.descendants[0])
                del self.descendants[0]
            


############################################################################################

    def slim(self, ancestors):
        parent = None
        totalAncestors=len(ancestors)
        sibling_left=None
        sibling_right=None

        # check if there is a space in destination node
        if totalAncestors:
            parent=ancestors[-1][0]
            parent_index = ancestors[-1][1]
            del ancestors[-1]
            if parent_index!=0:
                sibling_left = parent.descendants[parent_index-1]
            if parent_index < len(parent.descendants)-1:
                sibling_right = parent.descendants[parent_index + 1]

            #if left child have space put key in it
            if sibling_left and len(sibling_left.keys) < self.bptree.degree:
                self.lateral(parent, parent_index, sibling_left, parent_index - 1)
                return

            #if right child have space put key in it
            if sibling_right and len(sibling_right.keys) < self.bptree.degree:
                self.lateral(parent, parent_index, sibling_right, parent_index + 1)
                return

        # split the parent node since no vacancy in child

        sibl, push = self.split()
        if parent:
            parent.keys.insert(parent_index, push)
            parent.descendants.insert(parent_index + 1, sibl)
            if len(parent.keys) < parent.bptree.degree:
                return
            parent.slim(ancestors)
        else:
            #create new parent and new index
            parent=_BNode(self.bptree, descendants=[self])
            # parent_index=0
            self.bptree._root = parent
            parent.keys.insert(0, push)
            parent.descendants.insert(1, sibl)
            if len(parent.keys) < parent.bptree.degree:
                return
            parent.slim(ancestors)

############################################################################################################################


############################################### class BPlus leaf ########################################################

class _BPlusLeaf(_BNode):

    def __init__(self, bptree, keys=None, data=None, next=None):
        self.bptree = bptree
        if keys:
            self.keys=keys
        else:
            self.keys=[]
        if data:
            self.data = data
        else:
            self.data=[]
        self.next = next


#######################################################################################################

    def insert(self, index, key, data, ancestors):
        self.data.insert(index, data)
        self.keys.insert(index, key)
        totalKeys=len(self.keys)
        if totalKeys <= self.bptree.degree:
            return
        self.slim(ancestors)

#######################################################################################################

    def lateral(self, parent, parent_index, dest, dest_index):
        if parent_index < dest_index :
            dest.keys.insert(0, self.keys[-1])
            del self.keys[-1]
            dest.data.insert(0, self.data[-1])
            del self.data[-1]
            parent.keys[parent_index] = dest.keys[0]

        else:
            dest.keys.append(self.keys[0])
            del self.keys[0]
            dest.data.append(self.data[0])
            del self.data[0]
            parent.keys[dest_index] = self.keys[0]
            
            

#######################################################################################################

    def split(self):
        center = int(len(self.keys)/2)# // 2
        medn = self.keys[center - 1]
        sibl = type(self)(self.bptree,self.keys[center:len(self.keys)],self.data[center:len(self.data)],self.next)
        self.keys = self.keys[0:center]
        self.data = self.data[0:center]
        self.next = sibl
        return sibl, sibl.keys[0]

########################################### class BTree ############################################################

class BTree(object):
    BRANCH = _BNode
    LEAF = _BNode

    def __init__(self, degree):
        self.degree = degree
        self._bottom = self.LEAF(self)
        self._root = self.LEAF(self)
#######################################################################################################

    def getPath(self, item,current,ancestors):
        
        if getattr(current, "descendants", None):
            #find position of item in current keys
            keys=sorted(current.keys)
            index = 0
            for x in keys:
                if x < item:
                    index += 1
            ancestors.append((current, index))
            if index < len(current.keys) and current.keys[index] == item:
                return ancestors
            # current = current.descendants[index]
            return super(BPlusTree, self).getPath(item,current.descendants[index],ancestors)
        else:
            keys=sorted(current.keys)
            index = 0
            for x in keys:
                if x < item:
                    index += 1
            ancestors.append((current, index))
            return ancestors


############################################## class Bplus Tree #########################################################

class BPlusTree(BTree):
    LEAF = _BPlusLeaf

    def _find_key(self, key):
        ancestors=self.getPath(key)
        node = ancestors[len(ancestors)-1][0]
        index = ancestors[len(ancestors)-1][1]
        if index == len(node.keys):
            if node.next:
                return node.next.data[0]
            else:
                return False
        return node.keys[index]

#######################################################################################################

    def getPath(self, item):
        path = super(BPlusTree, self).getPath(item,self._root,[])
        node =path[len(path)-1][0]
        index = path[len(path)-1][1]
        try:
            while True:
                node = node.descendants[index]
                keys=sorted(node.keys)
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

# Count number of keys in between pair of keys
    def range_query(self, upper_bound, lower_bound):
        allKeys = []
        node = self._root
        # traverse to left most node
        try:
            while True:
                node = node.descendants[0]
        except AttributeError:
            pass
        # get all keys through the linked list keys=keys=values
        while node:
            allKeys+=node.keys
            node = node.next
        keys=allKeys
        keys=sorted(keys)
        count = 0
        for x in keys:
            if lower_bound <= x <= upper_bound:
                count += 1
        print(count)

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
        # get all keys through the linked list keys=keys=values
        while node:
            allKeys+=node.keys
            node = node.next
        keys=allKeys
        count = 0
        for x in keys:
            if key==x:
                count += 1
        print(count)

################################################################################################################

# Check if given key exists in tree
    def find_query(self,key):
        if self._find_key(key):
            print('YES')
        else:
            print('NO')


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
