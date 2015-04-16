""" Tree Module """


class DependencyNode(object):
    """ Dependency Node class """
    def __init__(self, value):
        """ Initialize Node """
        self._parent = None
        self._children = []
        self._value = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        """ Get Children """
        return self._children

    @property
    def child_count(self):
        """ Get child count """
        return len(self._children)

    def add_child(self, child):
        """ Add a child node """
        if not isinstance(child, DependencyNode):
            raise TypeError('"child" must be a DependencyNode')
        self._children.append(child)

    def add_children(self, children):
        """ Add multiple children """
        if not isinstance(children, list):
            raise TypeError('"children" must be a list')
        for child in children:
            self.add_child(child)

    def __str__(self):
        if not self._children:
            return "(%s)" % self._value

        children_strings = []
        for child in self._children:
            children_strings.append(str(child))
        return "(%s, [%s])" % (self._value, ", ".join(children_strings))


class DependencyTree(object):
    """ Dependency Tree class """
    def __init__(self, heads):
        """ Initialize Tree """
        self._heads = []
        if heads is not None:
            if not isinstance(heads, list):
                raise TypeError('"head" must be a list')
            for head in heads:
                self.add_head(head)

    @property
    def heads(self):
        """ Get heads """
        return self._heads

    @property
    def head_values(self):
        values = set()
        for head in self._heads:
            values.add(head.value)
        return values

    @property
    def head_count(self):
        """ Get head count """
        return len(self._heads)

    def __str__(self):
        head_strings = []
        for head in self._heads:
            head_strings.append("H" + str(head))
        return ", ".join(head_strings)

    def add_head(self, head):
        """ Add head Node """
        if not isinstance(head, DependencyNode):
            raise TypeError('"head" must be a DependencyNode')
        self._heads.append(head)

class DependencyTreeInstantiator(object):
    def __init__(self, tree):
        if not isinstance(tree, DependencyTree, constructors):
            raise TypeError('"tree" must be a DependencyTree')
        self._tree = tree
        self._instantiated = {}
        self._constructors = constructors
        self._executed = False

    @property
    def instantiated(self):
        if not self._executed:
            self.traverse()
        return self._instantiated

    def traverse(self):
        """ Traverse through tree heads and instantiate """
        for head in tree.heads:
            self._traverse(head)
        self._executed = True

    def _traverse(self, node):
        """ Recursive traverse method """
        name = node.value

        if name in self._instantiated:
            # Already instantiated
            return

        dependency_names = []
        for child in node.children:
            dependency_names.append(child.value)
            self._traverse(child)

        self._create_instance(name, dependency_names)

    def _create_instance(self, name, dependency_names):
        if name not in self._constructors:
            raise Exception('Missing constructor for "%s"' % name)
        constructor = self._constructors[name]

        # Create mapping to pass to format
        dependency_mapping = {}
        for dep_name in dependency_names:
            dependency_arg = 'self._instantiated["%s"]' % dep_name
            dependency_mapping[dep_name] = dependency_arg

        # new_instance = eval(
        #   'module({aerospike}, {mailer})'.format(
        #       aerospike=self._instantiated('aerospike')
        #       mailer=self._instantiated('mailer')
        #   )
        # )
        #
        # Create new instance
        new_instance = eval(
            constructor.format(*dependency_mapping)
        )

        # Add instance to instantiated dictionary
        self._instantiated[name] = new_instance
        return
