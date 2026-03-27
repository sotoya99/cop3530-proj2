from sys import prefix


class TSTNode:
    def __init__(self, char):
        self.char = char
        self.left = None
        self.mid = None
        self.right = None
        self.is_end_of_string = False

    def __init__(self):
        self.root = None

    #insert function
    def insert(self, word):
        self.root = self.insertHelper(self.root, word, 0)

    #search function
    def search(self, prefix):
        return self.searchHelper(self.root, prefix, 0)

    #helper function for insert
    def insertHelper(self, node, word, index):
        char = word[index]
        if node is None:
            node = TSTNode(char)

        if char < node.char:
            node.left = self.insertHelper(node.left, char, index)
        elif char > node.char:
            node.right = self.insertHelper(node.right, char, index)
        else:
            if index+1 == len(word):
                node.mid = self.insertHelper(node.mid, word, index+1)
            else:
                node.is_end_of_string = True
        return node
    
    #helper function for search
    def searchHelper(self, node, word, index):
        if node is None:
            return None
        char = word[index]
        if char < node.char:
            return self.searchHelper(node.left, word, index)
        elif char > node.char:
            return self.searchHelper(node.right, word, index)
        else:
            if index == len(word)-1:
                return node
            return self.searchHelper(node.mid, word, index+1)