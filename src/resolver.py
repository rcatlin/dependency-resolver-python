""" Resolver module """


class CircularDependencyError(Exception):
    """ Raised when a circular dependency graph is detected """
    def __init__(self, nodes, *args):
        path = nodes.join('->')
        self.message = "Circular Depedency Detected: %s" % path


class Resolver(object):
    """ Resolves graph """

    def solve(self, nodes):
        """ Solve graph into Solution """
        # Verify nodes type
        if not isinstance(nodes, dict):
            raise TypeError('"nodes" must be a dictionary')

        # Check for circular dependencies and get levels dictionary
        initial_dependencies = tuple(nodes.keys)
        levels = detect_circle_and_get_levels(nodes, initial_dependencies)

        # Return Solution
        return Solution(nodes, levels)

    def detect_circle_and_get_levels(self, nodes=[], dependencies=(),
                                     traveled=[], level=0, levels=[]):
        """
            Recursively iterate over nodes checking
            if we've traveled to that node before.
        """
        # Verify nodes and traveled types
        if not isinstance(nodes, dict):
            raise TypeError('"nodes" must be a dictionary')
        if not isinstance(traveled, dict):
            raise TypeError('"traveled" must be a dictionary')

        # We're done if dependencies is empty. We've traveled everywhere!
        if not dependencies:
            return

        # Recursively iterate over nodes
        levels = []
        for name in dependencies.iteritems():
            if name in traveled:
                raise CircularDependencyError(traveled + [name])

            # Add name to levels
            if level not in levels:
                levels[level] = ()
            levels[level].append()

            # Add node name to traveled list
            traveled.append(name)

            # Make recursive call
            self.detect_circle(nodes, dependencies, traveled,
                               level + 1, levels)

        return levels


class Solution(object):
    """ Resolver Solution for stepping through graph """
    def __init__(self, nodes={}, levels=[]):
        # Verify nodes and levels types
        if not isinstance(nodes, dict):
            raise TypeError('"nodes" must be a dictionary')
        if not isinstance(levels, dict):
            raise TypeError('"nodes" must be a dictionary')

        self.nodes = nodes
        self.levels = levels
        self._num_levels = len(levels)
        self._current_level = 0

    def free(self):
        """ Return free nodes at current level """
        if self._current_level in levels:
            return self.levels[self._current_level]
        return ()

    def forward(self):
        """ Move up a level in the graph """
        self._current_level += 1

    def backward(self):
        """ Move down a level in the graph """
        self._current_level -= 1

    @property
    def current_level(self):
        """ Return current level """
        return self._current_level

    @property
    def num_levels(self):
        """ Return number of levels """
        return self._num_levels
