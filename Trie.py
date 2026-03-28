from typing import Dict, List


class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def autocomplete(self, prefix):
        node = self.search(prefix)
        if not node:
            return []

        results = []
        if node.is_end_of_word:
            results.append(prefix)
        self.collectWords(node, prefix, results)
        return results

    def collectWords(self, node, prefix, results):
        for char in sorted(node.children.keys()):
            next_node = node.children[char]
            next_prefix = prefix + char

            if next_node.is_end_of_word:
                results.append(next_prefix)

            self.collectWords(next_node, next_prefix, results)
