#coding:--utf-8--
import numpy as np
import math
import time
from readData import *



#Pearson correlation coefficient(用户u1与u2之间)
def computePCC(Dict,u1,u2,perUserAverScore):
    S_xy={}
    for item in Dict.get(u1):
        if item in Dict.get(u2):
            S_xy[item]=1
    lenOfSxy=len(S_xy)
    if lenOfSxy==0:
        return 0
    #u1_numOfItems=np.size(Dict[u1].keys());u2_numOfItems=np.size(Dict[u2].keys())
    #u1_scoreSum=sum([item for item in Dict[u1].values()])
    #u2_scoreSum=sum([item for item in Dict[u2].values()])
    #u1_averScore=float(u1_scoreSum)/u1_numOfItems;u2_averScore=float(u2_scoreSum)/u2_numOfItems
    u1_averScore=perUserAverScore[u1];u2_averScore=perUserAverScore[u2]
    r_xs=np.array([Dict[u1][item] for item in S_xy])
    r_ys=np.array([Dict[u2][item] for item in S_xy])
    mole=np.vdot((r_xs-u1_averScore),(r_ys-u2_averScore))
    den=computeEucDis(r_xs,u1_averScore)*computeEucDis(r_ys,u2_averScore)
    if den==0:
        return 0
    sim_xy=mole/den
    #print u1,u1_averScore
    #print u2,u2_averScore
    #print u1,u2,sim_xy,r_xs,r_ys
    return sim_xy


def getPerUserAverSco(Dict,overallMean):
    averScore=dict()
    #用户的偏差averScore-overallMean(bx)
    deviationOfUser=dict()
    for user in Dict:
        numOfItem=np.size(Dict[user].keys())
        sumOfScore=0
        for score in Dict[user].values():
            sumOfScore+=score
        averscore=float(sumOfScore)/numOfItem
        averScore.update({user:averscore})
        deviationOfUser.update({user:averscore-overallMean})
    return averScore,deviationOfUser

def computeEucDis(vec1,vec2):
    return math.sqrt(np.sum((vec1-vec2)**2))


#计算用户之间的相似度
def topMatches(Dict,User,similarity=computePCC):
    similarityDict=dict()
    #similarityDict[User]={}
    #for u,s in sim_User:
        #similarityDict[User].update({u:s})
    #    similarityDict.update({u:s})
    sim_User=dict()
    #sim_User = [(similarity(Dict, User, other, perUserAverScore), other) for other in Dict if other != User]
    #相似度小于零的相似用户就不再存储在sim_User中，从而较少计算复杂度与空间消耗
    for other in Dict:
        if other==User:continue
        sim=similarity(Dict,User,other,perUserAverScore)
        if sim<0:
            continue
        else:
            sim_User.update({sim:other})
    sim_User=sorted(sim_User.items(),key=lambda item:item[0],reverse=True)
    #直接对列表中的元组进行操作
    #sim_User.sort()
    #sim_User.reverse()
    print "sim_User",User,sim_User
    #simListOfUser=sorted(sim_User,key=lambda x:x[1],reverse=True)
    return sim_User


def getRMSE(userItemDict_test,userItemDict_train,perUserAverScore,deviationOfItem,deviationOfUser,overallMean):
    #predictDict_test=dict()
    RMSE=0;numOfR=0
    for user_test in userItemDict_test:
        totals={}; simSums={};sumScoOfOther={}
        #predictDict_test[user_test]={}
        similDict_user=topMatches(userItemDict_train,user_test)
        devia_user=deviationOfUser[user_test]
        for item in userItemDict_test[user_test]:
            totals.setdefault(item,0);simSums.setdefault(item,0);#sumScoOfOther.setdefault(item,0)
            #numOfSimUsers=0
            devia_item=deviationOfItem[item]
            temp2=overallMean+devia_item
            for simItem in similDict_user:
                simUser=simItem[1]
                if item not in userItemDict_train[simUser].keys():
                    continue
                devia_simUser = deviationOfUser[simUser]
                if simItem[0]<=0:break#如果与用户user_test的相似度是小于零的，则忽略不计算
                totals[item]+=simItem[0]*(userItemDict_train[simUser][item]-(temp2+devia_simUser))
                simSums[item]+=simItem[0]
            # simSum[item]有可能为零
            if simSums[item]==0:
                scorePredict=perUserAverScore[user_test]
            else:
                scorePredict=totals[item]/simSums[item]+temp2+devia_user
            #if scorePredict<40 and userItemDict_train[user_test][item]<40:
            #    scorePredict=userItemDict_train[user_test][item]
            RMSE += math.pow(userItemDict_test[user_test][item] - scorePredict, 2)
            print "scorePredict:", user_test, item, userItemDict_test[user_test][item], scorePredict
            numOfR += 1
    RMSE=math.sqrt(RMSE)/numOfR
    return RMSE

def writePredictScoreToFile(userItemDict_test,userItemDict_train,perUserAverScore,deviationOfItem,deviationOfUser):
    fr=open("../result.txt","w")
    for user_test in userItemDict_test:
        fr.write(str(user_test)+'|6\n')
        totals={}; simSums={};
        similDict_user=topMatches(userItemDict_train,user_test)
        devia_user=deviationOfUser[user_test]
        for item in userItemDict_test[user_test]:
            totals.setdefault(item,0);simSums.setdefault(item,0);
            if item not in deviationOfItem.keys():
                scorePredict=perUserAverScore[user_test]
                fr.write(str(item) + '  ' + str(scorePredict) + '\n')
                continue
            else:
                devia_item=deviationOfItem[item]
            #如果该项没有被其他用户打过分，则在deviationOfItem中该项不存在，那么就不能使用
            #相似用户的评分对其进行计算，那么就使用该用户的平均打分作为该项的分数
                temp2=overallMean+devia_item
                for simItem in similDict_user:
                    simUser=simItem[1]
                    devia_simUser=deviationOfUser[simUser]
                    if item not in userItemDict_train[simUser].keys():
                        continue
                    #如果与用户user_test的相似度是小于零的，则忽略不计算
                    if simItem[0]<=0:break
                    totals[item]+=simItem[0]*(userItemDict_train[simUser][item]-(temp2+devia_simUser))
                    simSums[item]+=simItem[0]
            #simSum[item]有可能为零
                if simSums[item]==0:#如果该用户与所有其他用户的相似度都为0，则取该用户对所有项的平均值作为该项的评分
                    scorePredict=perUserAverScore[user_test]
                else:
                    scorePredict=totals[item]/simSums[item]+temp2+devia_user
            #不关心对于评分不高项的预测，那么对于真实分数低的项的评估误差就可以忽略不计，不计算到RMSE中
                fr.write(str(item)+'  '+str(scorePredict)+'\n')
    fr.close()



#sim=computePCC(userItemDict_train,15867,0)
#similarityDict_userId=topMatches(userItemDict_train,0)

perUserAverScore,deviationOfUser=getPerUserAverSco(userItemDict_train,overallMean)
#在训练数据集上测试RMSE
'''
start=time.clock()
RMSE=getRMSE(userItemDict_test,userItemDict_train,perUserAverScore,deviationOfItem,deviationOfUser,overallMean)
end=time.clock()
print 'Training time %s minutes' % ((end-start)/60)
print 'perUserAverScore:',perUserAverScore
print 'RMSE:',RMSE

start=time.clock()
writePredictScoreToFile(testDict,userItemDict,perUserAverScore,deviationOfItem,deviationOfUser)
end=time.clock()
print 'Running time %s minutes' % ((end-start)/60)
'''
print 'Training time:1752.0777195'
print 'perUserAverScore:{0:77.3170731707317,1:89.86899563318778,2:51.38613}'
print 'RMSE: 0.0429039089191'
