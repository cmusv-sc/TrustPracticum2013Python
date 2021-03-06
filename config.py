DB_NAME = "dblp"
COLLECTION_NAME = "documents"

# Trust value Weights
 # Publication Weight
Pw=0.3			
Cw=0.5

# Publication Channel Weights
alphaArticle=0.075
alphaBook=0.125
alphaInCollection=0.15
alphaInProceeding=0.175
alphaMasterThesis=0.1
alphaPhdThesis=0.125
alphaProceeding=0.2
alphaWWW=0.05

# Twitter Trust Parameter
sigmaRetweet=0.2

# Time Scale (in Years)
recentYears=7				
intermediateYears=7

# Time Scale Weights	
tRecent=0.5
tIntermediate=0.3
tOld=0.2

#Mapping from types to alpha weights. Should refactor later on.
type2weights = {"article" : alphaArticle, "inproceedings" :alphaInProceeding, "proceedings" : alphaProceeding, "book" : alphaBook, "phdthesis" : alphaMasterThesis, "mastersthesis" :alphaPhdThesis, "www" : alphaWWW, "incollection" : alphaInCollection}
