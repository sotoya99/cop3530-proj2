import csv
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Dict, List

class TrieNode:
    def __init__(self, char=""):
        self.char = char
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word = False
        
    @property
    def is_end(self):
        return self.is_end_of_word
    
    @is_end.setter
    def is_end(self, value):
        self.is_end_of_word = value
              
class Trie:
    def __init__(self):
        self.root = TrieNode("ROOT")
        self.total_words = 0
        self.total_nodes = 1

    @property
    def node_count(self):
        return self.total_nodes

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode(ch)
                self.total_nodes += 1
            node = node.children[ch]
        if not node.is_end_of_word:
            node.is_end_of_word = True
            self.total_words += 1

    def build(self, words: List[str]) -> None:
        for word in words:
            self.insert(word)

    def _collect_words(
        self,
        node: TrieNode,
        current: str,
        results: List[str],
        limit: int,
        stats: dict,
    ) -> None:
        if len(results) >= limit:
            return

        stats["nodes_visited"] += 1

        if node.is_end_of_word:
            results.append(current)
            if len(results) >= limit:
                return

        for ch in sorted(node.children.keys()):
            self._collect_words(node.children[ch], current + ch, results, limit, stats)
            if len(results) >= limit:
                return

    def autocomplete(self, prefix: str, limit: int = 10) -> dict:
        start = time.perf_counter()
        node = self.root
        path = []
        stats = {"nodes_visited": 0}

        for ch in prefix:
            stats["nodes_visited"] += 1
            path.append(ch)
            if ch not in node.children:
                end = time.perf_counter()
                return {
                    "suggestions": [],
                    "nodes_visited": stats["nodes_visited"],
                    "search_time_ms": (end - start) * 1000,
                    "path": path,
                    "found_prefix": False,
                }
            node = node.children[ch]

        suggestions: List[str] = []
        self._collect_words(node, prefix, suggestions, limit, stats)
        end = time.perf_counter()
        return {
            "suggestions": suggestions,
            "nodes_visited": stats["nodes_visited"],
            "search_time_ms": (end - start) * 1000,
            "path": path,
            "found_prefix": True,
        }

    # find node where search ends returns path
    def find_prefix_node(self, prefix):
        
        # start at root
        path = [self.root]
        node = self.root
        
        # go through each char
        for char in prefix:
            
            if char not in node.children: return None, path, False
            
            node = node.children[char]
            path.append(node)
            
        return node, path, True
    
    # get next "n" words
    def get_suggestions(self, prefix, limit):
        
        results = []
        
        # find ending node
        node, path, found = self.find_prefix_node(prefix)
        
        if not found: return results, path, False
        
        if node.is_end_of_word: results.append(prefix)
        
        # track nodes
        stats = {"nodes_visited": 0}
        
        # collect words from children
        for char in sorted(node.children.keys()):
            self._collect_words(node.children[char], prefix + char, results, limit, stats)
            if len(results) >= limit:
                break
        
        # remove dups
        final = []
        seen = set()
        
        for word in results:
            if word not in seen:
                final.append(word)
                seen.add(word)
            
            if len(final) >= limit: break
            
        return final, path, True

class TSTNode:
    def __init__(self, char):
        self.char = char
        self.left = None
        self.mid = None
        self.right = None
        self.is_end_of_string = False
        
    @property
    def eq(self):
        return self.mid
    
    @eq.setter
    def eq(self, value):
        self.mid = value

    @property
    def is_end(self):
        return self.is_end_of_string

    @is_end.setter
    def is_end(self, value):
        self.is_end_of_string = value

class TST:
    def __init__(self):
        self.root = None
        self.node_count = 0

    #insert function
    def insert(self, word):
        if not word: return
        self.root = self.insertHelper(self.root, word, 0)

    #search function
    def search(self, prefix):
        if not prefix: return None
        return self.searchHelper(self.root, prefix, 0)

    #helper function for insert
    def insertHelper(self, node, word, index):
        char = word[index]
        if node is None:
            node = TSTNode(char)
            self.node_count += 1

        if char < node.char:
            node.left = self.insertHelper(node.left, word, index)
        elif char > node.char:
            node.right = self.insertHelper(node.right, word, index)
        else:
            if index+1 < len(word):
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
        
    #autocomplete function
    def autocomplete(self, prefix):
        node = self.search(prefix)
        if not node:
            return []
        
        results = []
        if node.is_end_of_string:
            results.append(prefix)
        self.collectWords(node.mid, prefix, results, 999999)
        return results

    #helper function to collect all words with a given prefix
    def collectWords(self, node, prefix, results, limit):
        if not node or len(results) >= limit:
            return 
        
        self.collectWords(node.left, prefix, results, limit)

        next_prefix = prefix + node.char
        if node.is_end_of_string:
            results.append(next_prefix)
            if len(results) >= limit:
                return

        self.collectWords(node.mid, next_prefix, results, limit)

        if len(results) >= limit:
            return

        self.collectWords(node.right, prefix, results, limit)

    # find node where search ends returns path
    def find_prefix_node(self, prefix):
        
        # start at root
        path = []
        node = self.root
        index = 0

        # continue while prefix has chars left
        while node is not None and index < len(prefix):
            char = prefix[index]

            # move left or right
            if char < node.char:
                path.append((node, "L"))
                node = node.left

            elif char > node.char:
                path.append((node, "R"))
                node = node.right

            # match
            else:
                path.append((node, "E"))

                if index == len(prefix) - 1: return node, path, True

                index += 1
                node = node.mid

        # not found
        return None, path, False

    # get next "n" words for prefix
    def get_suggestions(self, prefix, limit):
        
        results = []
        
        # find ending node for prefix
        node, path, found = self.find_prefix_node(prefix)

        if not found: return results, path, False
        
        if node.is_end_of_string: results.append(prefix)
        
        self.collectWords(node.mid, prefix, results, limit)

        # remove dups
        final = []
        seen = set()

        for word in results:
            if word not in seen:
                final.append(word)
                seen.add(word)

            if len(final) >= limit: break

        return final, path, True

# loads list of words
def load_words_from_file(filename):
    
    words = []

    # open csv file and read words from "word" column
    with open(filename, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        
        if "word" not in reader.fieldnames:
            raise ValueError('Incorrect file.')
        
        # normalize each word
        for row in reader:
            word = row["word"].strip().lower()
            
            if word == "": continue
            if not word.isalpha(): continue
            
            words.append(word)
            
        return words

class App:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Trie vs TST Comparison")
        self.width = 1200
        self.height = 800
        self.root.geometry(f"{self.width}x{self.height}")
        self.myFont = "Arial"

        self.words = []
        self.trie = None
        self.tst = None

        self.trie_path = []
        self.tst_path = []

        self.create_ui()

    # creates user interaction bar and status bar
    def create_control_bar(self):

        self.controls_frame = tk.Frame(self.frame)
        self.controls_frame.pack(fill="x")

        #labels at columns 0, 3, 5
        tk.Label(self.controls_frame, text="CSV File:", font=(self.myFont, 10, "bold")).grid(row=0, column=0) 
        tk.Label(self.controls_frame, text="Prefix:", font=(self.myFont, 10, "bold")).grid(row=0, column=3)
        tk.Label(self.controls_frame, text="Suggestions:", font=(self.myFont, 10, "bold")).grid(row=0, column=5)
        
        # buttons at columns 2, 7
        self.load_button = ttk.Button(self.controls_frame,text="Load Words and Build Trees", command=self.load_and_build)
        self.load_button.grid(row=0, column=2)
        
        self.search_button = ttk.Button(self.controls_frame, text="Search", command=self.search_prefix)
        self.search_button.grid(row=0, column=7)
        
        # inputs at column 1, 4, 6
        self.csv_input = tk.Entry(self.controls_frame, width=28, font=(self.myFont, 10))
        self.csv_input.grid(row=0, column=1, padx=(0, 10))
        self.csv_input.insert(0, "words.csv")

        self.prefix_input = tk.Entry(self.controls_frame, width=16, font=(self.myFont, 10))
        self.prefix_input.grid(row=0, column=4, padx=(0, 12))
        self.prefix_input.insert(0, "")

        self.max_suggestions_input = tk.Entry(self.controls_frame, width=6, font=(self.myFont, 10))
        self.max_suggestions_input.grid(row=0, column=6, padx=(0, 12))
        self.max_suggestions_input.insert(0, "5")

        # status bar
        self.status_frame = tk.Frame(self.frame)
        self.status_frame.pack(fill="x")
        self.status_label = tk.Label(self.status_frame, text="No file loaded", font=(self.myFont, 10, "bold"), anchor="w", justify="left")
        self.status_label.pack(fill="x", pady=(0, 6))
        
    # creates left and right tree frames    
    def create_mid_frame(self):
        
        self.panels_frame = tk.Frame(self.frame)
        self.panels_frame.pack(fill="both", expand=True)

        self.left_card = tk.Frame(self.panels_frame, bd=1, relief="solid")
        self.left_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.right_card = tk.Frame(self.panels_frame, bd=1, relief="solid")
        self.right_card.pack(side="right", fill="both", expand=True, padx=(8, 0))
    
    # constructs trie frame
    def create_trie_frame(self):
    
        # header label
        tk.Label(self.left_card, text="TRIE", font=(self.myFont, 25, "bold")).pack()
        
        # results label
        self.trie_results_label = tk.Label(self.left_card,text="",font=(self.myFont, 10, "bold"),anchor="center",justify="center")
        self.trie_results_label.pack(fill="x", pady=(8, 4))
        
        # filler
        tk.Label(self.left_card, text="").pack()
        
        # next words header label
        tk.Label(self.left_card, text="Next Words", font=(self.myFont, 12, "bold")).pack(pady=(0, 4))

        # next words listbox
        self.trie_listbox = tk.Listbox(self.left_card, font=(self.myFont, 10), height=1)
        self.trie_listbox.pack(fill="x", expand=False, padx=12, pady=(0, 10))

        # path label
        tk.Label(self.left_card, text="Path", font=(self.myFont, 12, "bold")).pack()
        
        # filler
        tk.Label(self.left_card, text="").pack()
        
        # lower path frame
        self.trie_canvas_frame = tk.Frame(self.left_card)
        self.trie_canvas_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # add scroll bar to path frame
        self.trie_scroll = tk.Scrollbar(self.trie_canvas_frame, orient="vertical")
        self.trie_scroll.pack(side="right", fill="y")

        # create canvas for path drawing
        self.trie_canvas = tk.Canvas(self.trie_canvas_frame, height=420, yscrollcommand=self.trie_scroll.set)
        self.trie_canvas.pack(side="left", fill="both", expand=True)
        
        # connect scroll bar to canvas
        self.trie_scroll.config(command=self.trie_canvas.yview)
      
    # constructs tst frame                  
    def create_tst_frame(self):
        
        # header label
        tk.Label(self.right_card, text="TST", font=(self.myFont, 25, "bold")).pack()
        
        # results label
        self.tst_results_label = tk.Label(self.right_card,text="",font=(self.myFont, 10, "bold"),anchor="center",justify="center")
        self.tst_results_label.pack(fill="x", pady=(8, 4))
        
        # filler
        tk.Label(self.right_card, text="").pack()
        
        # next words header label
        tk.Label(self.right_card, text="Next Words", font=(self.myFont, 12, "bold")).pack(pady=(0, 4))

        # next words listbox
        self.tst_listbox = tk.Listbox(self.right_card,font=(self.myFont, 10),height=1)
        self.tst_listbox.pack(fill="x", expand=False, padx=12, pady=(0, 10))
        
        # path label
        tk.Label(self.right_card, text= "Path", font=(self.myFont, 12, "bold")).pack()
        tk.Label(self.right_card, text="L= Left, R= Right, E= Equal", font=(self.myFont, 10)).pack()

        # lower path frame
        self.tst_canvas_frame = tk.Frame(self.right_card, bg="white")
        self.tst_canvas_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # add scroll bar to path frame
        self.tst_scroll = tk.Scrollbar(self.tst_canvas_frame, orient="vertical")
        self.tst_scroll.pack(side="right", fill="y")

        # create canvas for path drawing
        self.tst_canvas = tk.Canvas(self.tst_canvas_frame, height=420, highlightthickness=0, yscrollcommand=self.tst_scroll.set)
        self.tst_canvas.pack(side="left", fill="both", expand=True)
        
        # connect scroll bar to canvas
        self.tst_scroll.config(command=self.tst_canvas.yview)
     
    # create ui 
    def create_ui(self):
        
        # create main frame
        self.frame = tk.Frame(self.root, padx=12, pady=12)
        self.frame.pack(fill="both", expand=True)

        # build ui sections
        self.create_control_bar()
        self.create_mid_frame()
        self.create_trie_frame()
        self.create_tst_frame()
      
    # load csv file and build trees  
    def load_and_build(self):
        
        filename = self.csv_input.get().strip()

        # filename blank popup
        if filename == "":
            messagebox.showerror("Error", "Enter filename.")
            return

        try:
            # set status bar and load words
            self.status_label.config(text="Loading word list...")
            self.root.update_idletasks()
            
            self.words = load_words_from_file(filename)
            
            self.status_label.config(text=f"Loaded {len(self.words):,} words. Building Trie and TST")
            self.root.update_idletasks()
            
            # build trie and calculate time taken
            self.trie = Trie()
            start_trie = time.perf_counter()
            for word in self.words: self.trie.insert(word)
            trie_build_time = time.perf_counter() - start_trie
        
            # build tst and calculate time taken
            self.tst = TST()
            start_tst = time.perf_counter()
            for word in self.words: self.tst.insert(word)
            tst_build_time = time.perf_counter() - start_tst

            # update status labels with results
            trie_time = f"build time: {trie_build_time:.4f} secs"
            tst_time = f"build time: {tst_build_time:.4f} secs"
            trie_nodes = f"nodes created: {self.trie.node_count:}"
            tst_nodes = f"nodes created: {self.tst.node_count:}"
            
            # self.results_label.config(text=f"Trie: {trie_time}, {trie_nodes} | TST: {tst_time}, {tst_nodes}")
            self.trie_results_label.config(text=f"{trie_time}, {trie_nodes}")
            self.tst_results_label.config(text=f"{tst_time}, {tst_nodes}")
            self.status_label.config(text=f"Completed")
            self.root.update_idletasks()

            self.clear_all()

        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    # search button clicked
    def search_prefix(self):
        
        # trees are empty
        if self.trie is None or self.tst is None:
            messagebox.showerror("Error", "Load word file")
            return

        # get and verify user prefix input 
        prefix = self.prefix_input.get().strip().lower()
        if prefix == "" or not prefix.isalpha():
            messagebox.showerror("Error", "Enter a non numeric prefix.")
            return

        # get and verify user max suggestions input
        try:
            limit = int(self.max_suggestions_input.get().strip())
            if limit <= 0:
                messagebox.showerror("ERRPR", "Must be greater than 0.")
                return
        except:
            messagebox.showerror("ERROR", 'Enter a positive integer in the "Suggestions Box"')
            return

        # Trie, time and get suggestions
        start = time.perf_counter()
        trie_suggestions, trie_path, trie_found = self.trie.get_suggestions(prefix, limit)
        trie_time_end = time.perf_counter() - start
        
        # TST, time and get suggestions
        start = time.perf_counter()
        tst_suggestions, tst_path, tst_found = self.tst.get_suggestions(prefix, limit)
        tst_time_end = time.perf_counter() - start

        # clear all and draw paths
        self.clear_all()
        self.draw_trie_path(trie_path, trie_found)
        self.draw_tst_path(tst_path, tst_found)

        # insert next "n" words into suggestion box
        self.trie_listbox.insert(tk.END, ", ".join(trie_suggestions) if trie_suggestions else "No Words Found")
        self.tst_listbox.insert(tk.END, ", ".join(tst_suggestions) if tst_suggestions else "No Words Found")

        # update status bar and 
        self.status_label.config(text=(f"Word Searched: '{prefix}'"))

        # populate results in each tree frame
        trie_time = f"time {trie_time_end * 1000:.4f} ms"
        trie_nodes = f"navigated {len(trie_path)} nodes"
        trie_results = f"results {len(trie_suggestions)}"
        self.trie_results_label.config(text=f"{trie_time}, {trie_nodes}, {trie_results}")

        tst_time = f"time {tst_time_end * 1000:.4f} ms"
        tst_nodes = f"navigated {len(tst_path)} nodes"
        tst_results = f"results {len(tst_suggestions)}"
        self.tst_results_label.config(text=f"{tst_time}, {tst_nodes}, {tst_results}")
        
    # clear all entries
    def clear_all(self):
        
        self.trie_canvas.delete("all")
        self.trie_listbox.delete(0, tk.END)

        self.tst_canvas.delete("all")
        self.tst_listbox.delete(0, tk.END)

    # draws path taken in trie
    def draw_trie_path(self, path, found):
        
        # settings
        pos_x = self.trie_canvas.winfo_width() / 2 + 10
        pos_y = 30
        offset_y = 75
        radius = 20

        # draw each node
        for i, node in enumerate(path):
            x = pos_x
            y = pos_y + i * offset_y

            # connecting line
            if i > 0:
                prev_y = pos_y + (i - 1) * offset_y
                self.trie_canvas.create_line(x, prev_y + radius, x, y - radius, width=1)

            # set valid node to light blue, final node yellow if search failed
            fill_color = "lightblue"
            if i == len(path) - 1 and not found: fill_color = "yellow"
            
            # draw and label node
            self.trie_canvas.create_oval(x - radius, y - radius, x + radius, y + radius,fill=fill_color)
            label = node.char
            label_size = 11
            if label.strip().upper() == "ROOT": label_size = 8
            self.trie_canvas.create_text(x, y, text=label, font=(self.myFont, label_size, "bold"))
            
            # update scroll area
            self.check_scroll_area(self.trie_canvas)

    # draws path takin in tst
    def draw_tst_path(self, path, found):

        # settings
        pos_x = self.tst_canvas.winfo_width() / 2 + 10
        pos_y = 40
        offset_y = 60
        offset_x = 55
        radius = 20
        offset_direction = 28

        positions = []
        current_x = pos_x
        current_y = pos_y

        # add starting node
        positions.append((path[0][0], path[0][1], current_x, current_y))

        # determine position for remaining nodes
        for i in range(1, len(path)):
            node, direction = path[i]
            move = path[i - 1][1]

            if move == "L": current_x -= offset_x
            elif move == "R": current_x += offset_x
            elif move == "E": pass

            current_y += offset_y
            positions.append((node, direction, current_x, current_y))

        # draw each node and line
        for i, (node, direction, x, y) in enumerate(positions):

            if i > 0:
                prev_x = positions[i - 1][2]
                prev_y = positions[i - 1][3]

                self.tst_canvas.create_line(prev_x, prev_y + radius, x, y - radius, width=1)

            # set valid node to light red, final node yellow if search failed
            node_color = "lightcoral"
            if i == len(positions) - 1 and not found: node_color = "yellow"

            # draw and label node
            self.tst_canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill= node_color)
            self.tst_canvas.create_text(x, y, font=(self.myFont, 11, "bold"), text=node.char)

            # direction labels
            dir_color = "black"
            label_x = x + offset_direction
            label_y = y

            if direction == "L":
                dir_color = "blue"
                label_x = x - offset_direction
            elif direction == "R":
                dir_color = "red"
                label_x = x + offset_direction
            elif direction == "E":
                dir_color = "green"
                label_x = x + offset_direction

            # draw direction labels
            self.tst_canvas.create_text(label_x, label_y, text=direction,fill=dir_color,font=(self.myFont, 10, "bold"))

        # update scroll area
        self.check_scroll_area(self.tst_canvas)

    # updates scroll region
    def check_scroll_area(self, canvas):
        
        # refresh size
        canvas.update_idletasks()
        
        # get bounding box for all drawn items
        bounding_box = canvas.bbox("all")

        # canvas empty reset, else set scrollable area
        if bounding_box is None: canvas.configure(scrollregion=(0, 0, 0, 0))
        else:
            padding = 20
            x1, y1, x2, y2 = bounding_box
            canvas.configure(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))

def main():
    root = tk.Tk()
    app = App(root)
    app.clear_all()
    root.mainloop()

if __name__ == "__main__":
    main()
