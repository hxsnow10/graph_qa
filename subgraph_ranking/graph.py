#encoding=utf-8

# V1
class GraphRankClient(object):

    def __init__(self):
        pass
    
    def query_key_size(self, key):
        """O(1)"""
        raise NotImplementedError
        
    def query_key(self, keys, node_type=None, th=0.3, topn=300):
        """query GraphBase with key
        Args
        ===
        keys: a dict of word
        node_type: object/relation
        th: min score
        topn:int

        Return
        ===
        return [(node_id, node_type, score)...]
            node_id should unique;
            node_type indicate type of node_id, for example, object/relation;
            score is dict of keys, {key1:v1, key2:v2, ...}
        """
        raise NotImplementedError
     
    def query_score(self, node_id, keys):
        raise NotImplementedError
        
    def query_direct_linked(self, node_id, max_d):
        """query GraphBase with node_id
        return [(node_id_, d)...], where d<=max_d
            node_id and node_id_ should with shortest distance=d in New Graph Space.
            for exampe, node_a-(rel_e)->node_b, then d(a,e)=1, d(e,b)=1, d(a,b)=2
        
        transfer max_d for efficiency, GB may save this result directly.
        """
        raise NotImplementedError

    def subgragh_ranking(self, keys, max_d):
        #matched_nodes = self.query(keys, "object")
        #matched_rels = self.query(keys, "relation")
        sizes={}
        for key in keys:
            sizes[key]=self.query_key_size(key)
            sizes=sorted(sizes.iteritems(), a=lambda x:x[0])
        
        # find init nodes by small key
        key, size  = sizes[0]
        matched_nodes = self.query([key])
        
        def maxf():
            return 1000
        def deffloat():
            return defaultdict(maxf)
        nexts=defaultdict(deffloat)
        node2score={}
        
        for node_id, node_type, score in matched_nodes:
            node2score[node_id]=query_score(id_, keys)
        
        cut_max_d=max_d/2
        for node_id, node_type, score in matched_nodes:
            linked=self.query_direct_linked(node_id, cut_max_d)
            for id_, d in linked:
                nexts[node_id][id_]=d
                nexts[id_][node_id]=d
                if id_ not in node2score:
                    node2score[id_]=query_score(id_, keys)

        nodes=node2score.keys()
        nexts2=defaultdict(deffloat)
        for n1 in nodes:
            for n2 in nodes:
                if n1==n2:nexts2[n1][n2]==0
                if n2 in nexts[n1]:
                    nexts2[n1][n2]=nexts[n2][n1]=nexts[n1][n2]
                else:
                    for n3 in set(nexts[n1]) & set(nexts[n2]):
                        nexts2[n1][n2]=nexts2[n2][n1]=min(nexts[n1][n3]+nexts[n3][n2], nexts[n1][n2])
        key2nodes=[set([]) for _ in range(len(keys))]
        key2index={key:k for k,key in enumerate(keys)}
        for node in node2score:
            for key,score in enumerate(node2score[node]):
                if score>0:
                    key2nodes[key2index[key]].add(node)
        self.search(nexts2, key2nodes, node2score)
    
    def search(self, nexts, nodes_set, node2score):
        searched=set([])
        end_searched_states=[]
        TODO=[(None,)*len(node_set)]
        index=0

        def expand(state):
            node_candidates = reduce(lambda x,y:x|y, [set(nexts[node].keys()) for node in state if node], set([]))
            for set_index in range(len(state)):
                if state[set_index]: continue
                node_candidates_ = node_candidates & nodes_set[set_index]
                for node in node_candiadates_:
                    state_=deepcopy(state)
                    state_[set_index]=node
                    yield state_

        def get_score(state):
            nodes=set(state)
            scores = [node2score[node] for node in nodes]
            compute score from scores
            
        while index<len(TODO):
            state=TODO[index]
            k=0
            for new_state in expand(state):
                if new_state in searched:continue
                TODO.append(new_state)
                searched.add(new_state)
                k+=1
            searched.add(state)
            if k==0:
                end_searched_states.append(state)
            index+=1
        states=end_searched_states
        scores=[get_score(state) for state in states]
        rval=sorted(zip(states, scores), lambda x:x[1], reverse=True)
        return rval
