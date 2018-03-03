# coding: utf-8
#     PURPOSE:   验证码下载
#     VERSION:   0.0.1
#     AUTHOR:    Lin Leiying
#     MODIFIED:  2018/01/10 08:00


import requests,os

#         http://pica.arongjie.com/11/20180110/201801101449/6019014491132101086.jpg
#         http://pica.arongjie.com/11/20180110/201801101449/60190144911321000001.jpg
#         http://pica.arongjie.com/11/20180110/201801101449/6019014491132100001.jpg
#         http://pica.arongjie.com/11/20180110/201801101449/6019014491132100658.jpg
#         http://pica.arongjie.com/11/20180110/201801101449/6019014491132100012.jpg
base_url='http://pica.arongjie.com/11/20180110/201801101449/601901449113210' #00000 +'.jpg'
sess = requests.session()
for i in range(0,10000):
    num_i=str(i).zfill(4)
    new_url=base_url+num_i+'.jpg'
    r=sess.get(new_url,stream=True)
    if r.status_code==200:
        print new_url
        f = open(os.getcwd() + '/sam/' + num_i+'.gif', "wb")
        for chunk in r.iter_content(chunk_size=204800):
            if chunk:
                f.write(chunk)
    else:
        print num_i,':',404,new_url
        # if chunk:
        #     pct = round(doneGetingsize * 100 / toGetsize, 2)
        #     logger.debug('Writing Chunk:' + str(doneGetingsize) + '/' + str(toGetsize) + '/' + str(pct) + '%')
        #     f.write(chunk)
        #     doneGetingsize += 204800

