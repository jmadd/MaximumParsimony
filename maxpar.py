import sys
from networkx import nx
from ete2 import Tree
import argparse
import datetime
from random import randint as rand

inf = 10e10
final = []

def hamming(s1, s2):
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))

def ancestor(s1, s2):
    return s1

def fullyConnectedGraph(V):
    gr = nx.Graph()
    for i in xrange(0,len(V)):
        for j in xrange(i+1,len(V)):
            gr.add_edge(V[i],V[j], weight=hamming(final[ V[i] ], final[ V[j] ]) )
    return gr

def cheapestEdge(G):
    cheapest = inf
    node = (None, None)
    for u,v in G.edges():
        if cheapest > G[u][v]['weight']:
            node = (u,v)
            cheapest = G[u][v]['weight']
    return node

def ObtainAnc(A, tree, V):
    for u, v in A:
        anc = ancestor(final[u], final[v])
        final.append(anc)
        tree[ len(final) - 1 ] = [u,v]
        V.append( len(final) - 1 )

def maxPar(V):
    tree = {}
    for i in V:
        final.append(i)
    V = range(0, len(final))
    head = None
    while len(V) > 1:
        G = fullyConnectedGraph(V)
        T = nx.minimum_spanning_tree(G)
        A = []
        while T.number_of_edges() > 0:
            u,v = cheapestEdge(T)
            A.append( (u,v) )
            if T.number_of_nodes() == 2:
                head = len(final)
            T.remove_node(u)
            T.remove_node(v)
        V = T.nodes()
        ObtainAnc(A,tree, V)
    return head, tree

def addToTree(tree, T, node):
    for next in T.neighbors(node):
        if node not in tree:
            tree[node] = []
        tree[node].append(next)
    T.remove_node(node)
    if node in tree:
        for next in tree[node]:
            addToTree(tree, T, next)

def maxPar2Approx(V):
    tree = {}
    for i in V:
        final.append(i)
    V = range(0, len(final))
    head = 0
    G = fullyConnectedGraph(V)
    T = nx.minimum_spanning_tree(G)
    addToTree(tree, T, head)

    # adjust nodes to add transition of generations
    for node in tree:
        final.append(final[node])
        tree[node].append(node)
    return head, tree


def cost(node, tree):
    total = 0
    child = None
    if node in tree:
        for child in tree[node]:
            if ( twoapprox and final[child] != final[node]) or not twoapprox:
                total = total + hamming(final[node], final[child]) + cost( child, tree )
    return total

def add_to_tree(node, tree, match, t):
    if node in tree:
        for child in tree[node]:
            str_child = final[child]
            node_1 = t.add_child( name=match[str_child] if str_child in match else "NOT KNOWN" )
            if ( twoapprox and str_child != final[node]) or not twoapprox:
                add_to_tree( child, tree, match, node_1 )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='finds the maximum parsimony tree')
    parser.add_argument('infile', type=str,
                       help='input file')
    parser.add_argument('--twoapprox', dest='trigger', action='store_const',
                       const=True, default=False,
                       help='use two approx algorithm (default: use custom algorithm)')
    args = parser.parse_args()
    twoapprox = args.trigger
    infile = args.infile
    x = []
    taxon = []
    match = {}
    for line in open(infile):
        line = str(line)
        if '>' in line: 
            taxon.append(line[1:-1])
        else:
            x.append(line[:-1])
            match[x[-1]] = taxon[-1]
    a = datetime.datetime.now()
    if twoapprox:
        head, tree = maxPar2Approx(x)
    else:
        head, tree = maxPar(x)
    b = datetime.datetime.now()
    c = b - a
    st = final[head]
    t = Tree(name="R")
    t = Tree( name=match[st] if st in match else "NOT KNOWN" )
    add_to_tree(head, tree, match, t)
    t.ladderize()
    newick = t.write(format=1).replace(":1", "").replace("1", "")
    print t.get_ascii(show_internal=True)
    print newick
    print "Cost:", cost(head, tree)
    print "Time (seconds): ", c.microseconds / float(1e6)
