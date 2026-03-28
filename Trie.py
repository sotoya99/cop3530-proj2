import csv
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.total_words = 0
        self.total_nodes = 1

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
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


class TSTNode:
    def __init__(self, char):
        self.char = char
        self.left = None
        self.mid = None
        self.right = None
        self.is_end_of_string = False


class TST:
    def __init__(self):
        self.root = None
        self.total_words = 0
        self.total_nodes = 0

    def insert(self, word):
        if not word:
            return
        self.root = self.insertHelper(self.root, word, 0)

    def search(self, prefix):
        if not prefix:
            return None
        return self.searchHelper(self.root, prefix, 0)

    def insertHelper(self, node, word, index):
        char = word[index]
        if node is None:
            node = TSTNode(char)
            self.total_nodes += 1

        if char < node.char:
            node.left = self.insertHelper(node.left, word, index)
        elif char > node.char:
            node.right = self.insertHelper(node.right, word, index)
        else:
            if index + 1 < len(word):
                node.mid = self.insertHelper(node.mid, word, index + 1)
            else:
                if not node.is_end_of_string:
                    node.is_end_of_string = True
                    self.total_words += 1
        return node

    def searchHelper(self, node, word, index):
        if node is None:
            return None
        char = word[index]
        if char < node.char:
            return self.searchHelper(node.left, word, index)
        elif char > node.char:
            return self.searchHelper(node.right, word, index)
        else:
            if index == len(word) - 1:
                return node
            return self.searchHelper(node.mid, word, index + 1)

    def autocomplete(self, prefix):
        node = self.search(prefix)
        if not node:
            return []

        results = []
        if node.is_end_of_string:
            results.append(prefix)
        self.collectWords(node.mid, prefix, results)
        return results

    def collectWords(self, node, prefix, results):
        if not node:
            return

        self.collectWords(node.left, prefix, results)

        next_prefix = prefix + node.char
        if node.is_end_of_string:
            results.append(next_prefix)

        self.collectWords(node.mid, next_prefix, results)
        self.collectWords(node.right, prefix, results)

    def autocomplete_with_metrics(self, prefix, limit=10):
        start = time.perf_counter()
        path = []
        counter = {"nodes_visited": 0}
        node = self._search_with_metrics(self.root, prefix, 0, counter, path) if prefix else None

        if not node:
            end = time.perf_counter()
            return {
                "suggestions": [],
                "nodes_visited": counter["nodes_visited"],
                "search_time_ms": (end - start) * 1000,
                "path": path,
                "found_prefix": False,
            }

        results = []
        if node.is_end_of_string:
            results.append(prefix)

        self._collect_words_with_metrics(node.mid, prefix, results, limit, counter)
        end = time.perf_counter()
        return {
            "suggestions": results[:limit],
            "nodes_visited": counter["nodes_visited"],
            "search_time_ms": (end - start) * 1000,
            "path": path,
            "found_prefix": True,
        }

    def _search_with_metrics(self, node, word, index, counter, path):
        if node is None:
            return None

        counter["nodes_visited"] += 1
        path.append(node.char)
        char = word[index]

        if char < node.char:
            return self._search_with_metrics(node.left, word, index, counter, path)
        if char > node.char:
            return self._search_with_metrics(node.right, word, index, counter, path)
        if index == len(word) - 1:
            return node
        return self._search_with_metrics(node.mid, word, index + 1, counter, path)

    def _collect_words_with_metrics(self, node, prefix, results, limit, counter):
        if not node or len(results) >= limit:
            return

        counter["nodes_visited"] += 1
        self._collect_words_with_metrics(node.left, prefix, results, limit, counter)

        next_prefix = prefix + node.char
        if node.is_end_of_string and len(results) < limit:
            results.append(next_prefix)

        self._collect_words_with_metrics(node.mid, next_prefix, results, limit, counter)
        self._collect_words_with_metrics(node.right, prefix, results, limit, counter)

def normalize_word(word: str) -> str:
    return "".join(ch.lower() for ch in word.strip() if ch.isalpha())



def load_words_from_csv(file_path: str) -> List[str]:
    words = []
    seen = set()

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if "word" not in reader.fieldnames:
            raise ValueError("CSV must include a 'word' column.")

        for row in reader:
            raw_word = row.get("word", "")
            word = normalize_word(raw_word)
            if word and word not in seen:
                seen.add(word)
                words.append(word)

    return words

class AutocompleteApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Autocomplete Using Trie and Ternary Search Trees")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 650)

        self.file_path = tk.StringVar()
        self.prefix_var = tk.StringVar()
        self.result_count_var = tk.StringVar(value="10")
        self.dataset_size_var = tk.StringVar(value="Dataset not loaded")

        self.words: List[str] = []
        self.trie = Trie()
        self.tst = TST()

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Autocomplete Using Trie and Ternary Search Trees",
            font=("Arial", 18, "bold"),
        )
        title.pack(anchor="w", pady=(0, 12))

        top_bar = ttk.Frame(container)
        top_bar.pack(fill="x", pady=(0, 12))

        ttk.Label(top_bar, text="CSV File:").pack(side="left")
        ttk.Entry(top_bar, textvariable=self.file_path, width=52).pack(side="left", padx=6)
        ttk.Button(top_bar, text="Browse", command=self.browse_file).pack(side="left", padx=(0, 6))
        ttk.Button(top_bar, text="Load CSV", command=self.load_dataset).pack(side="left", padx=(0, 20))

        ttk.Label(top_bar, text="Prefix:").pack(side="left")
        ttk.Entry(top_bar, textvariable=self.prefix_var, width=18).pack(side="left", padx=6)
        ttk.Label(top_bar, text="Return Count:").pack(side="left")
        ttk.Entry(top_bar, textvariable=self.result_count_var, width=8).pack(side="left", padx=6)
        ttk.Button(top_bar, text="Search", command=self.run_search).pack(side="left")

        ttk.Label(container, textvariable=self.dataset_size_var, font=("Arial", 10, "italic")).pack(anchor="w", pady=(0, 12))

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self.trie_frame = self._create_result_panel(content, "Trie Results")
        self.trie_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.tst_frame = self._create_result_panel(content, "Ternary Search Tree Results")
        self.tst_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    def _create_result_panel(self, parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(parent, text=title, padding=12)
        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(0, weight=1)

        stats_frame = ttk.Frame(frame)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        stats_frame.columnconfigure(1, weight=1)

        ttk.Label(stats_frame, text="Nodes Visited:").grid(row=0, column=0, sticky="w")
        nodes_value = ttk.Label(stats_frame, text="-")
        nodes_value.grid(row=0, column=1, sticky="w")

        ttk.Label(stats_frame, text="Search Time (ms):").grid(row=1, column=0, sticky="w")
        time_value = ttk.Label(stats_frame, text="-")
        time_value.grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Suggestions:").grid(row=1, column=0, sticky="w")
        suggestions = tk.Listbox(frame, height=12)
        suggestions.grid(row=2, column=0, sticky="nsew", pady=(4, 8))

        ttk.Label(frame, text="Path Taken:").grid(row=3, column=0, sticky="nw")
        path_box = tk.Text(frame, height=8, wrap="word")
        path_box.grid(row=4, column=0, sticky="nsew")

        frame.nodes_value = nodes_value
        frame.time_value = time_value
        frame.suggestions = suggestions
        frame.path_box = path_box
        return frame

    def browse_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if file_path:
            self.file_path.set(file_path)

    def load_dataset(self) -> None:
        path = self.file_path.get().strip()
        if not path:
            messagebox.showerror("Missing file", "Please choose a CSV file first.")
            return

        try:
            start_load = time.perf_counter()
            self.words = load_words_from_csv(path)

            self.trie = Trie()
            self.tst = TST()

            self.trie.build(self.words)
            self.tst.build(self.words)
            end_load = time.perf_counter()

            self.dataset_size_var.set(
                f"Loaded {len(self.words):,} unique words | Trie nodes: {self.trie.total_nodes:,} | "
                f"TST nodes: {self.tst.total_nodes:,} | Build time: {(end_load - start_load):.2f}s"
            )

            messagebox.showinfo("Success", f"Dataset loaded successfully with {len(self.words):,} words.")
        except Exception as exc:
            messagebox.showerror("Error loading dataset", str(exc))

    def run_search(self) -> None:
        if not self.words:
            messagebox.showwarning("No dataset", "Please load the dataset before searching.")
            return

        prefix = normalize_word(self.prefix_var.get())
        if not prefix:
            messagebox.showwarning("Missing prefix", "Please enter a valid alphabetic prefix.")
            return

        try:
            result_count = int(self.result_count_var.get())
            if result_count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid count", "Return count must be a positive integer.")
            return

        trie_result = self.trie.autocomplete(prefix, result_count)
        tst_result = self.tst.autocomplete_with_metrics(prefix, result_count)

        self._update_panel(self.trie_frame, trie_result)
        self._update_panel(self.tst_frame, tst_result)

    def _update_panel(self, panel: ttk.LabelFrame, result: dict) -> None:
        panel.nodes_value.config(text=str(result["nodes_visited"]))
        panel.time_value.config(text=f"{result['search_time_ms']:.4f}")

        panel.suggestions.delete(0, tk.END)
        if result["suggestions"]:
            for item in result["suggestions"]:
                panel.suggestions.insert(tk.END, item)
        else:
            panel.suggestions.insert(tk.END, "No suggestions found")

        panel.path_box.delete("1.0", tk.END)
        if result["path"]:
            panel.path_box.insert(tk.END, " -> ".join(result["path"]))
        else:
            panel.path_box.insert(tk.END, "No path available")


def main() -> None:
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    app = AutocompleteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
