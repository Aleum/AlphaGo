# -*- coding: ms949 -*-


from graphviz import Digraph
from go import *


styles = {
    'digraph': {
        'size': '1000,1000'
    },          
    'nodes': {
        'fontname': 'courier new',      
        'fontsize': '12'
    },
    'edges': {
        'fontname': 'courier new',         
        'fontsize': '12'
    }
}

def apply_styles(graph, styles):
    graph.node_attr.update(
        ('digraph' in styles and styles['digraph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph


def printnode(dot, node, parent):
    if node.type == 'StateNode':
        a = node.state.tostr()
        a_key = node.state.tostr2()
        #print "a_key : " + a_key
        #dot.node(a_key, a + " \: " + str(node.q))
        dot.node(a_key, a)
        if parent is not None:
            b = parent.parent.state.tostr()            
            b_key = parent.parent.state.tostr2()
            #print "b : " +  b
            #c = parent.action.tostr()
            c = parent.tostr()
            dot.edge(b_key, a_key, label=c)
            #dot.edge(a_key, b, label=c)
    
    for child in node.child:
        printnode(dot, child, node)
        

def printgraph(filepath, node):
    #print "drawing started"
    
    dot = Digraph(comment='The Round Table')
    dot = apply_styles(dot, styles)
    printnode(dot, node, None)
    dot.render(filepath, view=False)
    
    #print "ended"
    
    