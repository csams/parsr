from io import StringIO


class Node:
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        return self

    def set_parent(self, parent):
        self.parent = parent
        if parent:
            parent.children.append(self)
        return self

    def set_children(self, children):
        for c in self.children:
            c.parent = None

        self.children.clear()
        for c in children:
            self.add_child(c)
        return self

    def replace_child(self, old, new):
        self.children = [c if c != old else new for c in self.children]
        new.parent = self
        return self

    def __repr__(self):
        return self.__class__.__name__


def text_format(tree):
    out = StringIO()
    tab = " " * 2
    seen = set()

    def inner(cur, prefix):
        print(prefix + str(cur), file=out)
        if cur in seen:
            return

        seen.add(cur)

        next_prefix = prefix + tab
        for c in cur.children:
            inner(c, next_prefix)

    inner(tree, "")
    out.seek(0)
    return out.read()


def render(tree):
    print(text_format(tree))
