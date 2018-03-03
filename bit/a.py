# -*- coding:utf-8 -*-


from bitcoin import *

priv = sha256('some big long brainwallet password 12312 123123123131')
print '[priv key]:',priv
pub = privtopub(priv)
print '[pub key]:',pub
addr = pubtoaddr(pub)
print '[addr]:',addr

h = history(addr)
print h
'''
[priv key]: 92890b34d97fbbaac2ab7672c664fdab693c95e358a0e8b9d5ed4c3c15ddddaa
[pub key]: 049459ed731e0a96d84274bf224c449ad9ce823532dc8a81f9ea4a693eef507a966dba3a1c8860fac0ba68edf04f06984c9e966db0596e445bc484e779ffd32ffb
[addr]: 1HdBhV7AoydAc4RJwmFwpEQLjjsFpbwBJP
[]
'''
inputs = [{
            'output': 'cd6219ea108119dc62fce09698b649efde56eca7ce223a3315e8b431f6280ce7:0',
            'value': 1000
   }]

outs = [
    {'value': 900, 'address': '16iw1MQ1sy1DtRPYw3ao1bCamoyBJtRB4t'},
    {'address': '1FcbBw62FHBJKTiLGNoguSwkBdVnJQ9NUn', 'value': 50}
        ]

tx = mktx(inputs,outs)
print '[tx1]',tx
tx2 = sign(tx, 0, priv)
print '[tx2]',tx
tx3 = sign(tx2,1,priv)
print '[tx3]',tx

pushtx(tx3)