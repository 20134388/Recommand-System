# coding:--utf-8--
import numpy as np
import re

#读取训练数据，
def readTrainDataSet():
    fr=open('../train.txt')
    line=fr.readline()
    lineNumber=0
    userItemDict = dict()
    userId=0;overallMean=0;sumNumOfItem=0
    averScoreOfItem=dict()
    deviationOfItem=dict()
    numOfRankedUser=np.zeros(624961)
    while line:
        if isNumeric(line):
            temp=line.split('|')
            userId=int(temp[0])
            numOfItem=temp[1]
            #sumOfScore=0;numOfNext=0
            print userId,numOfItem
        else:
            temp=line.split('  ')
            itemId=int(temp[0])
            scoreOfItem=float(temp[1])
            #可能对某些电影item没有评过分np.size(averScoreOfItem.keys())=455309
            averScoreOfItem.setdefault(itemId, 0)
            averScoreOfItem[itemId]+=scoreOfItem
            numOfRankedUser[itemId]+=1
            overallMean+=scoreOfItem
            sumNumOfItem+=1
            #sumOfScore+=scoreOfItem
            #numOfNext+=1
            userItemDict=addTwoDimDict(userItemDict,userId,itemId,scoreOfItem)
        #if numOfNext==numOfItem:
        #    userItemDict[userId].update({-1:sumOfScore/numOfItem})
        line=fr.readline().strip()
        #lineNumber += 1
    fr.close()
    overallMean=overallMean/sumNumOfItem
    #这里的item都是用户评过分的，即使平均分为零
    for item in averScoreOfItem:
        averscore=averScoreOfItem[item]/numOfRankedUser[item]
        averScoreOfItem.update({item:averscore})
        deviationOfItem.update({item:averscore-overallMean})
    return userItemDict,overallMean,averScoreOfItem,deviationOfItem

#正则表达式
def isNumeric(str):
    p1=r"[0-9]*[|][0-9]*"
    pattern=re.compile(p1)
    return pattern.match(str)

#添加到二维字典中
def addTwoDimDict(theDict,key_a,key_b,val):
    if key_a in theDict:
        theDict[key_a].update({key_b:val})
    else:
        theDict.update({key_a:{key_b:val}})
    return theDict

#写入文件进行测试
def saveDataToFile(userItemDict):
    for i in range(3):
        fr=open("../user"+str(i)+".txt",'w')
        dict_user=userItemDict[i]
        for j in range(np.size(dict_user.keys())):
            fr.write(str(dict_user.keys()[j])+" "+str(dict_user.values()[j])+'\n')
        fr.close()

#将数据集划分为训练集与测试集
def splitToTrainAndTest(allUserItemDict,ratio):
    '''
    sumOfUsers=np.size(allUserItemDict.keys())
    numOfTest=sumOfUsers*ratio
    userItemDict_test=dict()
    userItemDict_train = allUserItemDict.copy()
    for i in range(int(numOfTest)):
        userItemDict_test.update({i:allUserItemDict[i]})
        userItemDict_train.pop(i)
    for j in range(np.size(userItemDict_train.keys())):
        userItemDict_train[j]=(userItemDict_train.pop(userItemDict_train.keys()[j])
    '''
    sumOfUsers=np.size(allUserItemDict.keys())
    numOfTrain=int(sumOfUsers*(1-ratio))
    numOfTest=sumOfUsers-numOfTrain
    userItemDict_train=dict()
    userItemDict_test=allUserItemDict.copy()
    for i in range(numOfTrain):
        userItemDict_train.update({i:allUserItemDict[i]})
        userItemDict_test.pop(i)
    for user in userItemDict_test:
        tempDict=userItemDict_test[user]
        #lenOfTempDict=np.size(tempDict.keys())
        lenOfTempDict=(624960+1)/2
        #numOfIter=0
        for key,value in tempDict.items():
            #numOfIter+=1
            #if numOfIter>lenOfTempDict/2:break
            if key<lenOfTempDict:
                #userItemDict_train[user].update({key:value})
                userItemDict_train=addTwoDimDict(userItemDict_train,user, key, value)
                userItemDict_test[user].pop(key)
    return userItemDict_train,userItemDict_test
#读取测试数据
def readTestDataSet():
    fr=open('../test.txt')
    testDict=dict()
    line=fr.readline().strip()
    userId=0
    while line:
        if isNumeric(line):
            temp=line.split('|')
            userId=int(temp[0])
            numOfItem=int(temp[1])
        else:
            itemId=int(line)
            scoreOfItem=0
            testDict=addTwoDimDict(testDict,userId,itemId,scoreOfItem)
        line=fr.readline().strip()
    fr.close()
    return testDict






testRatio=0.2
userItemDict,overallMean,averScoreOfItem,deviationOfItem=readTrainDataSet()
#saveDataToFile(userItemDict)
userItemDict_train,userItemDict_test=splitToTrainAndTest(userItemDict,testRatio)
#print userItemDict

testDict=readTestDataSet()


'''
t={0:{1:1,3:2},1:{3:4,4:2},2:{1:3,2:5,4:3,5:4,6:3},3:{2:4,3:1,5:3},4:{3:2,4:5,5:4,6:3},5:{1:5,5:2},
   6:{2:4,3:3,4:1},7:{1:3,4:4,6:2},8:{1:5,3:4,5:5},9:{2:2,3:3,6:3},10:{1:4,2:1,3:5,4:2,5:2,6:4},11:{2:3,5:5}}
userItemDict_train,userItemDict_test=splitToTrainAndTest(t,0.5)
print userItemDict_train
print userItemDict_test
'''