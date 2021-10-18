"""
Automatically perform numerical analysis of historical linguistics data
and create diagrams according to the Historical Glottometry method of
language genealogy (François & Kalyan 2017; http://hg.hypotheses.org/)

Isaac Stead, October 2021


"Given a candidate subgroup S, let us call p the number of innovations
that properly confirm its cohesion (i.e., those which contain the
whole of the subgroup as well as at least one language outside the
subgroup); and q the number of cross-cutting innovations.  Together, p
and q constitute all the relevant evidence needed to assess a
subgroup’s cohesiveness.  We define κ as follows:
      p + 1
κ = —————
    p + q + 1

Given this definition of cohesiveness, we define the subgroupiness
of a subgroup (called ς ‘sigma’).  In principle, subgroupiness
could simply be conceived as the product of epsilon and kappa —
that is, the number of exclusively shared innovations, weighted by
the subgroup’s cohesiveness rating. However, we wish to add a
final refinement to the results, by adding a strictness parameter
n, that would set the “penalty” for overlapping subgroups:
                                n
         n           (  p + 1  )
ς = ε · κ  = ε · (——————————)
                     (p + q + 1)

"""
from itertools import chain

from pandas import read_csv
from scipy.spatial.distance import pdist


def contains(s1, s2):
    larger, smaller = sorted([s1, s2], key=len, reverse=True)
    return set(smaller).issubset(set(larger))


def unique(seqs):
    count = {}
    for el in chain.from_iterable(seqs):
        if el in count:
            count[el] += 1
        else:
            count[el] = 1
    return [k for k, v in count.items() if v == 1]


def grouped_unique(seqs):
    count = {}
    for seq in seqs:
        for el in seq:
            if el in count: 
                count[el] += 1
            else:
                count[el] = 1
    seq_uniques = [k for k, v in count.items() if v == 1]
    groups = []
    for seq in seqs:
        group = []
        for el in seq_uniques:
            if el in seq:
                group.append(el)
        groups.append(group)
    return groups
        

class FeatureMatrix:

    def __init__(self, path):
        frame = read_csv(path, sep="\t")

        lang_feats = {l : list() for l in frame.columns[1:]}
        feat_langs = {i : list() for i in frame["Innovation"]}
    
        for row in frame.itertuples():
            innv = getattr(row, "Innovation")
            for lang in lang_feats.keys():
                if getattr(row, lang) == 1:
                    lang_feats[lang].append(innv)
                    feat_langs[innv].append(lang)

        self.lang_feats = lang_feats
        self.feat_langs = feat_langs
        self.feat_matrix = frame


    @property
    def languages(self):
        return self.lang_feats.keys()


    @property
    def features(self):
        return self.feat_langs.keys()


    def exclusive(self, languages):
        shared = []
        for feat, langs in self.feat_langs.items():
            if sorted(langs) == sorted(languages):
                shared.append(feat)
        return shared

    
    def supporting(self, languages):
        shared = []
        for feat, langs in self.feat_langs.items():
            if contains(languages, langs):
                shared.append(feat)
        return shared


    def conflicting(self, languages):
        # This could be modified to specify which conflicting features are
        # possessed by which input language using `grouped_unique`
        feats = [fs for l, fs in self.lang_feats.items() if l in languages]
        confl = unique(feats)
        return confl


    def cohesiveness(self, languages):
        n_supporting = len(self.supporting(languages))
        n_conflicting = len(self.conflicting(languages))
        return n_supporting / (n_supporting + n_conflicting)


    def subgroupiness(self, languages):
        # TODO: Allow specification of strictness parameter
        cohesiveness = self.cohesiveness(languages)
        exclusively_shared = len(self.exclusive(languages))
        return cohesiveness * exclusively_shared
