from networkx import nx

inf = 10e10
final = []

def hamming(s1, s2):
	return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))

def ancestor(s1, s2):
	return s1
	# return sum( ch1 == ch2 for ch1, ch2 in zip(s1, s2))

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
		# Z = T.nodes()
		V = T.nodes()
		for u, v in A:
			anc = ancestor(final[u], final[v])
			final.append(anc)
			tree[ len(final) - 1 ] = (u,v)
			V.append( len(final) - 1 )
	return head, tree

def cost(node, tree):
	total = 0
	child = None
	if node in tree:
		child1, child2 = tree[node]
		total = total + hamming( final[node], final[child1] ) + hamming( final[node], final[child2] ) + cost(child1, tree) + cost(child2, tree)
	return total

if __name__ == '__main__':
	x = []
	for line in open('MaxPar.in'):
		x.append(line[:-1])
	print x
	head, tree = maxPar(x)
	print tree
	print cost(head, tree)