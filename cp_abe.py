from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import ABEnc, Input, Output
import time

# type annotations
pk = { 'g':G1, 'h':G1, 'f':G1, 'e_gg_alpha':GT }
mk = {'beta':ZR, 'g_alpha':G1 }
secret_key = { 'D':G1, 'Dj':G1, 'Djp':G1, 'S':str }
ct_t =  {'list_att':str, 'Ct':GT, 'C':G1, 'Cy':G1, 'Cyp':G1 }
debug = False

class abe(ABEnc):
    def __init__(self, groupObj):
        ABEnc.__init__(self)
        global util, group
        util = SecretUtil(groupObj, verbose=False)
        group = groupObj

    @Output(pk, mk)
    def setup(self):
        '''
        The setup algorithm takes no input
        It outputs the public parameters PK and a master key MK
        '''
        #choose a bilinear group G1 with genearator g
        #choose two random alpha, beta ∈ Z
        g = group.random(G1)
        alpha, beta = group.random(ZR),group.random(ZR)
        h = g ** beta
        f = g ** ~beta
        e_gg_alpha = pair(g,g**alpha)
        pk = {'g':g, 'h':h,'f':f,'e_gg_alpha':e_gg_alpha}
        mk = {'beta':beta,'g_alpha':g**alpha}
        return (pk, mk)
    
    @Input(pk, mk, [str])
    @Output(secret_key)
    def keygen(self, pk, mk, S):
        '''
        The key generation algorithm takes as input the master key MK and a set of attributes S
        that describe the key. It outputs a private key SK
        '''
        #choose random r and rj for each attr j ∈ S.
        r = group.random() 
        g_r = pk['g'] ** r  
        D = (mk['g_alpha']*g_r) ** (1/mk['beta'])
        Dj = {}
        Djp = {}
        for j in S:
            r_j = group.random()
            Dj[j] = g_r * (group.hash(j, G1) ** r_j)
            Djp[j] = pk['g'] ** r_j
        secret_key = { 'D':D, 'Dj':Dj, 'Djp':Djp, 'S':S }
        return secret_key
        
    @Input(pk, GT, str)
    @Output(ct_t)
    def encrypt(self, pk, M, policy_str):
        '''
        The encryption algorithm takes as input PK, a message M, and an access structure A over the universe of attributes
        The algorithm will encrypt M and produce a ciphertext CT
        '''
        #Convert string policy to standard type of BinNode
        policy = util.createPolicy(policy_str)
        #BinNode policy => list of attributes
        a_list = util.getAttributeList(policy)
        #s is coef a[0] of root node
        s = group.random(ZR)
        #Compute coef and value of poly q(x) for each node and attributes
        #calculate shares from given secret (a[0] of each poly)
        #returns a dict as {attribute:shares} pairs
        shares = util.calculateSharesDict(s, policy)

        Ct = (pk['e_gg_alpha'] ** s) * M
        C = pk['h']**s
        C_y, C_yp = {}, {}
        for i in shares.keys():
            #remove any trailing index or identifier separated by an underscore '_' of attributes
            j = util.strip_index(i)
            C_y[i] = pk['g'] ** shares[i]
            C_yp[i] = group.hash(j, G1) ** shares[i] 
        ct_t = {'list_att':a_list,'Ct':Ct,'C':C,'Cy':C_y,'Cyp':C_yp, 'policy':policy_str}
        return ct_t
    
    @Input(pk, secret_key, ct_t)
    @Output(GT)
    def decrypt(self, pk, sk, ct):
        '''
        The decryption algorithm takes as input the public parameters PK, a ciphertext CT, which contains 
        an access policy A, and a private key SK, which is a private key for a set S of attributes.
        If the set S of attributes satisfies the access structure A 
        then the algorithm will decrypt the ciphertext and
        return a message M
        '''
        #Convert string policy to standard type of BinNode
        policy = util.createPolicy(ct['policy'])
        #given policy tree and attributes S, determine whether the attributes satisfy the policy.
        #if not enough attributes to satisfy policy, return None otherwise, 
        #a pruned list of attributes to potentially recover the associated secret.
        pruned_list = util.prune(policy, sk['S'])
        if pruned_list == False:
            return False
        #recover coefficient over a binary tree where possible node types are OR = (1 of 2)
        #and AND = (2 of 2) secret sharing.
        #equivalent to recover coef of q(x) to recursive from leaf to root
        #z:list of larange coef for DecryptNode
        z = util.getCoefficients(policy)
        #A is result of a recursive algorithm from leaf node to root node
        A = 1 
        #i: list of prune attributes
        for i in pruned_list:
            #j:attributes equivalent to each leaf
            #k:attributes after remove index
            j = i.getAttributeAndIndex(); k = i.getAttribute()  
            A *= ( pair(ct['Cy'][j], sk['Dj'][k]) / pair(sk['Djp'][k], ct['Cyp'][j]) ) ** z[j]
        return ct['Ct'] / (pair(ct['C'], sk['D']) / A)
    
def cp_abe(attrs):
    pairing_group = PairingGroup('SS512')
    cpabe = abe(pairing_group)
    #access structure to encrypt message M
    access_policy = '((a or b) and (c or d)) and (e or (f or (g and h))'
    #print("Attributes =>", attrs); print("Policy =>", access_policy)
    #Setup algorithm to generate public key PK and master key MK
    (pk, mk) = cpabe.setup()
    #Keygen
    secret_key = cpabe.keygen(pk, mk, attrs)
    #Encrypt message
    rand_msg = pairing_group.random(GT)
    #if debug: print("msg =>", rand_msg)
    ct = cpabe.encrypt(pk, rand_msg, access_policy)
    #decrypt to obtain message
    rec_msg = cpabe.decrypt(pk, secret_key, ct)
    if rand_msg == rec_msg:
        return str(int.from_bytes(group.serialize(rec_msg), byteorder='big'))[:8]
    else:return None