import sys
from networkx import nx
from ete2 import Tree

inf = 10e10
final = []

# Finds the Hamming distance between two strings representing neucleotides
def hamming(s1, s2):
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))

# Gives desired ancestor of two child nodes.
# Simple solution: return child1 (s1)
def ancestor(s1, s2):
    return s1
    # return sum( ch1 == ch2 for ch1, ch2 in zip(s1, s2))

# Given a set of vertices, generates and returns a fully connected graph
def fullyConnectedGraph(V):
    gr = nx.Graph()
    for i in xrange(0,len(V)):
        for j in xrange(i+1,len(V)):
            gr.add_edge(V[i],V[j], weight=hamming(final[ V[i] ], final[ V[j] ]) )
    return gr

# Finds the cheapest edge in a graph G
def cheapestEdge(G):
    cheapest = inf
    edge = (None, None)
    for u,v in G.edges():
        if cheapest > G[u][v]['weight']:
            edge = (u,v)
            cheapest = G[u][v]['weight']
    return edge
  
def cost(node, tree):
    total = 0
    child = None
    if node in tree:
        child1, child2 = tree[node]
        total = total + hamming( final[node], final[child1] ) + hamming( final[node], final[child2] ) + cost(child1, tree) + cost(child2, tree)
    return total

def add_to_tree(node, tree, match, t):
    if node in tree:
        c1, c2 = tree[node]
        st1 = final[c1]
        st2 = final[c2]
        nd1 = t.add_child( name=match[st1] if st1 in match else "NOT KNOWN" )
        nd2 = t.add_child( name=match[st2] if st2 in match else "NOT KNOWN" )
        add_to_tree( c1, tree, match, nd1 )
        add_to_tree( c2, tree, match, nd2 )

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
        for u, v in A:
            anc = ancestor(final[u], final[v])
            final.append(anc)
            tree[ len(final) - 1 ] = (u,v)
            V.append( len(final) - 1 )
    return head, tree

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: <input file>"
        exit(-1)
    infile = sys.argv[1]
    x = []
    taxon = []
    match = {}
    for line in open(infile):
        if '>' in line: 
            taxon.append(line[:-1])
        else:
            x.append(line[:-1])
            match[x[-1]] = taxon[-1]
    head, tree = maxPar(x)
    st = final[head]
    t = Tree( name=match[st] if st in match else "NOT KNOWN" )
    add_to_tree(head, tree, match, t)
    t.ladderize()
    print t.get_ascii(show_internal=True)
    print "Cost:", cost(head, tree)
