# -*- coding: ms949 -*-

class Node(object):
    def __init__(self, parent):
        self.parent = parent
        self.children = {}
        self.q = 0
        self.n = 0
        self.type = 'notyet'        
        
        self.t = 't'


class ActionNode(Node):
    """
    A node holding an action in the tree.
    """
    def __init__(self, parent, action):
        super(ActionNode, self).__init__(parent)
        self.action = action
        self.n = 0
        self.type = 'ActionNode'
        self.active = 0 #확장했는지
        
        #Pa, Nv, Wv, Nr, Wr, Q
        self.Pa = 0 #P(s,a)  : prior probability
        self.Nv = 0 #Nv(s,a) : value net을 사용해 update한 횟수
        self.Wv = 0 #Wv(s,a) : Nv(s,a)로 계산한값
        self.Nr = 0 #Nr(s,a) : rollout policy를 사용해 update한 횟수
        self.Wr = 0 #Wr(s,a) : Nr(s,a)로 계산한값
#         self.Wms = 0 #Wms(s,a) : move score로 계산한값.
        self.Q = 0 #Q(s,a)  : (1-L)Wv/Nv + LWr/Nr
        
    @property
    def child(self):
        return [a for a in self.children.values()]

    def sample_state(self, real_world=False):
        """
        Samples a state from this action and adds it to the tree if the
        state never occurred before.

        :param real_world: If planning in belief states are used, this can
        be set to True if a real world action is taken. The belief is than
        used from the real world action instead from the belief state actions.
        :return: The state node, which was sampled.
        """
        if real_world:
            state = self.parent.state.real_world_perform(self.action)
        else:
            state = self.parent.state.perform(self.action)

        #여기 잘 모르겠음. 왜 있는건지. actionnode의 children이 왜 필요한가?
        #두번 생성하지 않으려고 한것 같음.
        if state not in self.children:
            self.children[state] = StateNode(self, state)
            
        #여기로 들어오는 일은 없음.
        if len(self.children) > 1:
            a = 1
        self.active = 1 #확장했는지

        if real_world:
            self.children[state].state.belief = state.belief

        return self.children[state]

    def __str__(self):
        return "Action: {}".format(self.action)
    def tostr(self):
        #return str(self.action) + "\n" + str(self.Nv) + ',' + str(self.Wv) + ',' + str(self.Nr) + ',' + str(self.Wr) + ',' + str(self.Wms) + ',' + str(round(self.Q, 2))
        return str(self.action) + "\n" + str(round(self.Pa, 3)) + ',' + str(self.Nv) + ',' + str(self.Wv) + ',' + str(self.Nr) + ',' + str(self.Wr) + ','  + str(round(self.Q, 2))
        #return str(self.action) + "\n" + str(self.Nv) + ',' + str(self.Nr)

'''
추가해야할 attr
P(s,a)  : prior probability
Nv(s,a) : value net을 사용해 update한 횟수
Nr(s,a) : rollout policy를 사용해 update한 횟수
Wv(s,a) : Nv(s,a)로 계산한값
Wr(s,a) : Nr(s,a)로 계산한값
Q(s,a)  : (1-L)Wv/Nv + LWr/Nr
'''
class StateNode(Node):
    """
    A node holding a state in the tree.
    """
    def __init__(self, parent, state):
        super(StateNode, self).__init__(parent)
        self.state = state
        self.reward = 0
        for action in state.actions:
            self.children[action] = ActionNode(self, action)
            #나중에 action에 대한 확률로 바꿔야함.
            self.children[action].Pa = 0.1
            
        self.type = 'StateNode'
        self.result_valuenet = 0
        self.result_rollout = 0
#         self.result_movescore = 0

    @property
    def untried_actions(self):
        """
        All actions which have never be performed
        :return: A list of the untried actions.
        """
        #return [a for a in self.children if self.children[a].n == 0]
        
        return [a for a in self.children if self.children[a].active == 0]
        
        #return [a for a in self.children.keys() if self.children[a].n == 0]
        #return [a for a in self.children.values() if self.children[a].n == 0]
    
    @property
    def tried_actions(self):        
        return [a for a in self.children.values() if self.children[a.action].active != 0]
        
    def get_tried_actions_count(self):        
        count = 0
        for anode in self.children.values() :
            if anode.active > 0:
                count += 1
                
        return count

    @property
    def child(self):
        return [a for a in self.children.values()]
    
    @untried_actions.setter
    def untried_actions(self, value):
        raise ValueError("Untried actions can not be set.")
    
    def is_terminal(self):
        #return False
        count = 0
        
        for anode in self.children.values() :
            if anode.active > 0:
                count = 1
                break
        
        return count == 0

    def __str__(self):
        return "State: {}".format(self.state)


def breadth_first_search(root, fnc=None):
    """
    A breadth first search (BFS) over the subtree starting from root. A
    function can be run on all visited nodes. It gets the current visited
    node and a data object, which it can update and should return it. This
    data is returned by the function but never altered from the BFS itself.
    :param root: The node to start the BFS from
    :param fnc: The function to run on the nodes
    :return: A data object, which can be altered from fnc.
    """
    data = None
    queue = [root]
    while queue:
        node = queue.pop(0)
        data = fnc(node, data)
        for child in node.children.values():
            queue.append(child)
    return data


def depth_first_search(root, fnc=None):
    """
    A depth first search (DFS) over the subtree starting from root. A
    function can be run on all visited nodes. It gets the current visited
    node and a data object, which it can update and should return it. This
    data is returned by the function but never altered from the DFS itself.
    :param root: The node to start the DFS from
    :param fnc: The function to run on the nodes
    :return: A data object, which can be altered from fnc.
    """
    data = None
    stack = [root]
    while stack:
        node = stack.pop()
        data = fnc(node, data)
        for child in node.children.values():
            stack.append(child)
    return data


def get_actions_and_states(node):
    """
    Returns a tuple of two lists containing the action and the state nodes
    under the given node.
    :param node:
    :return: A tuple of two lists
    """
    return depth_first_search(node, _get_actions_and_states)


def _get_actions_and_states(node, data):
    if data is None:
        data = ([], [])

    action_nodes, state_nodes = data

    if isinstance(node, ActionNode):
        action_nodes.append(node)
    elif isinstance(node, StateNode):
        state_nodes.append(node)

    return action_nodes, state_nodes